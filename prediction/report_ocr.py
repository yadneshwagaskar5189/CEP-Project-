"""
report_ocr.py
-------------
Extracts lab values from a photographed report.

DESIGN POSITION
---------------
Upload is the primary path, not a bolt-on. Photographing a document is a far
more widely held skill than reading one, and locating "Haemoglobin" on a
cluttered page is the actual literacy barrier - not typing the digits once you
have found them. OCR removes exactly that barrier.

The safety problem with OCR is that a misread is silent. Three mechanisms
handle it, and none of them require the user to read text:

1. VISUAL CONFIRMATION
   Every extracted value is shown beside the cropped image region it came from.
   The user compares a picture of a number to a number. That needs numeral
   recognition only. It is also easier to verify than a pre-filled form field,
   which people rubber-stamp.

2. PLAUSIBILITY GATE
   This domain has narrow valid ranges, which is a gift. Haemoglobin of 92 is
   impossible. A platelet count of 20 as an absolute value is impossible. A
   large share of OCR digit errors land outside physiology and are rejected
   without troubling the user at all.

3. ASYMMETRIC EVIDENCE (enforced in engine.escalate)
   The dangerous errors are the plausible ones - 15,000 platelets misread as
   150,000. So an OCR-derived value may RAISE urgency and may never LOWER it.
   If extraction is uncertain we fall back to symptoms alone and say so.

Manual entry remains available and is the same schema, because the manual form
IS the confirmation UI. OCR only ever pre-fills fields; it never writes straight
into the prediction input.
"""

import re

from ml_model.knowledge_base import LAB_TESTS

# ---------------------------------------------------------------------------
# availability
# ---------------------------------------------------------------------------

def ocr_available():
    """True if tesseract and its Python binding are both usable."""
    try:
        import pytesseract
        from PIL import Image  # noqa: F401
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# number parsing, including Indian conventions
# ---------------------------------------------------------------------------

_NUM = r"(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)"

# OCR routinely confuses these in numeric context.
_DIGIT_FIXES = str.maketrans({"O": "0", "o": "0", "l": "1", "I": "1",
                              "|": "1", "S": "5", "B": "8", "Z": "2"})


def _to_float(raw):
    """Parse '2,45,000' or '1.5 lakh' or '9.2' into a float."""
    if raw is None:
        return None
    text = str(raw).strip().translate(_DIGIT_FIXES)
    text = text.replace(",", "")

    lakh = bool(re.search(r"lakh|lac", text, re.I))
    text = re.sub(r"[^\d.]", "", text)
    if not text or text.count(".") > 1:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if lakh:
        value *= 100000
    return value


def normalise_value(test_key, value):
    """
    Apply unit conventions before validation.

    Indian reports commonly write platelets as '2.5' meaning 2.5 lakh, or as
    '2,50,000'. A bare '2.5' for platelets is lakh notation, not 2.5 cells.
    """
    test = LAB_TESTS.get(test_key)
    if test is None or value is None:
        return None
    if test.get("lakh_notation") and 0.3 <= value <= 15:
        return value * 100000
    return value


# ---------------------------------------------------------------------------
# plausibility gate
# ---------------------------------------------------------------------------

def validate_value(test_key, value):
    """
    Returns (status, value, message).
      ok         usable
      implausible physiologically impossible - reject, do not show as a result
      suspicious  possible typo, ask the user rather than acting on it
    """
    test = LAB_TESTS.get(test_key)
    if test is None:
        return "implausible", None, "Unknown test."
    if value is None:
        return "implausible", None, "Could not read a number."

    low, high = test["plausible"]
    if not (low <= value <= high):
        return ("implausible", None,
                f"{value:g} is outside anything physiologically possible for "
                f"{test['label']}, so it has been discarded.")

    # a value orders of magnitude off the normal range is likelier a typo
    n_low, n_high = test["normal"]
    if value < n_low / 20 or value > n_high * 20:
        return ("suspicious", value,
                f"{value:g} is a very long way from the usual range for "
                f"{test['label']}. Please double-check this figure.")

    return "ok", value, ""



# ---------------------------------------------------------------------------
# picking the RESULT number rather than the reference range
# ---------------------------------------------------------------------------
# Testing against a degraded phone photo showed the single most dangerous
# failure: on the line
#     Blood Sugar Fasting    148    mg/dL    70 - 99
# a blurred read grabbed 70 - the start of the REFERENCE RANGE - instead of 148.
# That turns a pre-diabetic result into a normal one. Falsely reassuring, and
# invisible.
#
# So: any number that forms part of an "a - b" pair is a range, never a result.
# ---------------------------------------------------------------------------

_RANGE = re.compile(_NUM + r"\s*(?:-|–|—|to)\s*" + _NUM, re.I)


def _pick_result_number(tail, test_key):
    """
    Return (raw_number, confidence, note) or None.

    confidence: high | medium | low
    """
    test = LAB_TESTS.get(test_key, {})

    # positions occupied by reference ranges - everything here is off limits
    banned = []
    for m in _RANGE.finditer(tail):
        banned.append((m.start(), m.end()))

    def in_range_span(pos):
        return any(a <= pos < b for a, b in banned)

    candidates = []
    for m in re.finditer(_NUM + r"\s*(lakh|lac)?", tail, re.I):
        if in_range_span(m.start()):
            continue
        raw = m.group(0).strip()
        val = normalise_value(test_key, _to_float(raw))
        if val is None:
            continue
        candidates.append((m.start(), raw, val))

    if not candidates:
        return None

    # the result column comes before the unit and reference columns
    pos, raw, val = candidates[0]

    note = ""
    confidence = "high"

    # if the value coincides with a reference-range endpoint elsewhere on the
    # line, we may still have grabbed the wrong column
    for m in _RANGE.finditer(tail):
        lo = normalise_value(test_key, _to_float(m.group(1)))
        hi = normalise_value(test_key, _to_float(m.group(2)))
        if lo is not None and abs(val - lo) < 1e-6:
            confidence = "low"
            note = ("This may have been read from the reference range column "
                    "rather than your result. Please check it against the report.")
        elif hi is not None and abs(val - hi) < 1e-6:
            confidence = "low"
            note = ("This may have been read from the reference range column "
                    "rather than your result. Please check it against the report.")

    # ANY abnormal value must be confirmed.
    #
    # Rationale, from measured failures: a value inside the normal range adds no
    # flag and therefore changes nothing, so a misread there is harmless. A value
    # outside the normal range is precisely what drives urgency. Testing on a
    # degraded photo produced a platelet count misread as 1,035,000 when the true
    # figure was 105,000 - high instead of low - which would have silently
    # discarded a dengue warning.
    #
    # So confirmation effort is tied to decision impact: abnormal always asks.
    if confidence == "high" and test.get("normal"):
        n_low, n_high = test["normal"]
        if val < n_low or val > n_high:
            confidence = "medium"
            side = "below" if val < n_low else "above"
            note = (f"This reads as {side} the usual range, which is what decides "
                    f"how urgent your result is. Please check it against the report "
                    f"before continuing.")
        if val < n_low / 4 or val > n_high * 4:
            confidence = "low"
            note = ("This is a very long way from the usual range. Misreading a "
                    "decimal point or a comma here is common, so please check it "
                    "digit by digit.")

    return raw, confidence, note


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------

def _preprocess(pil_image):
    """Light clean-up. Phone photos of reports are usually low contrast."""
    try:
        import cv2
        import numpy as np
        from PIL import Image

        img = np.array(pil_image.convert("L"))
        # upscale small photos - tesseract wants roughly 300 dpi
        h, w = img.shape
        if max(h, w) < 1600:
            scale = 1600 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        img = cv2.bilateralFilter(img, 7, 50, 50)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 31, 12)
        return Image.fromarray(img)
    except Exception:
        return pil_image


def extract_from_image(file_or_path):
    """
    Read a report image and return candidate values with the text they came from.

    Returns:
        {
          "available": bool,
          "found":   [ {test, label, value, raw_line, status, message, confidence} ],
          "rejected":[ {test, raw_line, message} ],
          "text":    full extracted text (not stored, only used for this request)
        }
    """
    if not ocr_available():
        return {"available": False, "found": [], "rejected": [], "text": "",
                "error": "OCR is not installed on this server. Please enter the "
                         "values by hand instead."}

    import pytesseract
    from PIL import Image

    try:
        image = Image.open(file_or_path)
        image.load()
    except Exception:
        return {"available": True, "found": [], "rejected": [], "text": "",
                "error": "That file could not be opened as an image."}

    prepared = _preprocess(image)
    try:
        text = pytesseract.image_to_string(prepared, config="--psm 6")
    except Exception as exc:
        return {"available": True, "found": [], "rejected": [], "text": "",
                "error": f"Could not read the image ({exc.__class__.__name__}). "
                         "Try a clearer, flatter photo in good light."}

    if len(text.strip()) < 20:
        # retry once with the unprocessed image; thresholding sometimes hurts
        try:
            text = pytesseract.image_to_string(image, config="--psm 6")
        except Exception:
            pass

    found, rejected = _scan_text(text)
    return {"available": True, "found": found, "rejected": rejected, "text": text}


def _scan_text(text):
    """Match each known test's aliases against the extracted lines."""
    found, rejected = [], []
    seen = set()

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    for key, test in LAB_TESTS.items():
        if key in seen:
            continue
        for alias in sorted(test["aliases"], key=len, reverse=True):
            pattern = re.compile(
                r"\b" + re.escape(alias).replace(r"\ ", r"\s+") + r"\b", re.I
            )
            hit = None
            for line in lines:
                if not pattern.search(line):
                    continue
                tail = line[pattern.search(line).end():]
                picked = _pick_result_number(tail, key)
                if picked is None:
                    continue
                raw, confidence, conf_note = picked
                value = normalise_value(key, _to_float(raw))
                status, value, message = validate_value(key, value)
                if conf_note and status == "ok":
                    status, message = "suspicious", conf_note
                hit = {"test": key, "label": test["label"], "value": value,
                       "unit": test["unit"], "raw_line": line[:120],
                       "raw_number": raw.strip(), "status": status,
                       "confidence": confidence, "message": message,
                       "normal_text": test.get("normal_text", "")}
                break
            if hit:
                if hit["status"] == "implausible":
                    rejected.append({"test": key, "label": test["label"],
                                     "raw_line": hit["raw_line"],
                                     "message": hit["message"]})
                else:
                    found.append(hit)
                seen.add(key)
                break
    return found, rejected


def confirmed_values(posted):
    """
    Build the final {test: value} map from what the user confirmed on the
    confirmation screen. Anything unconfirmed is dropped - OCR output never
    reaches the model without a human having looked at it.
    """
    values, warnings = {}, []
    for key in LAB_TESTS:
        if posted.get(f"confirm_{key}") != "on":
            continue
        raw = posted.get(f"value_{key}", "").strip()
        if not raw:
            continue
        value = normalise_value(key, _to_float(raw))
        status, value, message = validate_value(key, value)
        if status == "implausible":
            warnings.append(message)
            continue
        if status == "suspicious":
            warnings.append(message)
        values[key] = value
    return values, warnings
