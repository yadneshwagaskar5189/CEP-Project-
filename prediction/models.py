from django.db import models


class DiseaseInfo(models.Model):
    """
    Plain-language information shown after an assessment.
    Seeded from ml_model/disease_data.py, editable in the admin.

    NOTE: there is deliberately no "medicines to take" field. See the docstring
    in ml_model/disease_data.py for why. The `avoid` field does the opposite job
    and is safe even when the prediction is wrong.
    """

    URGENCY_CHOICES = [
        ("routine", "Worth seeing a doctor, but no rush"),
        ("prompt", "See a doctor in the next day or two"),
        ("urgent", "See a doctor today"),
        ("emergency", "Go to hospital now"),
    ]

    name = models.CharField(max_length=140, unique=True)
    about = models.TextField()
    precautions = models.TextField(help_text="One precaution per line.")
    avoid = models.TextField(
        blank=True,
        verbose_name="Drug safety warnings",
        help_text="What NOT to take. One per line. Never list medicines to take.",
    )
    tests = models.TextField(
        blank=True,
        verbose_name="Tests to ask for",
        help_text="One test per line.",
    )
    specialisation = models.CharField(
        max_length=80,
        help_text="Must match a Specialisation name so hospital referral works.",
    )
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default="routine")
    sensitive = models.BooleanField(
        default=False,
        help_text="Mental health conditions. Results are presented with support "
                  "resources first rather than a checklist.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Condition information"
        verbose_name_plural = "Condition information"

    def __str__(self):
        return self.name

    def precaution_list(self):
        return [l.strip() for l in self.precautions.splitlines() if l.strip()]

    def avoid_list(self):
        return [l.strip() for l in self.avoid.splitlines() if l.strip()]

    def test_list(self):
        return [l.strip() for l in self.tests.splitlines() if l.strip()]


class SymptomCheck(models.Model):
    """
    Anonymous log of each assessment.

    Stores no personal information and no uploaded files. It exists so the
    project can report which conditions people in an area are checking for,
    which is the awareness half of a Community Engagement Project.
    """

    symptoms = models.TextField(help_text="Comma separated symptom keys.")
    predicted_disease = models.CharField(max_length=140, blank=True)
    confidence = models.FloatField(default=0)
    urgency = models.CharField(max_length=20, blank=True)
    red_flag = models.CharField(max_length=40, blank=True)
    used_labs = models.BooleanField(default=False)
    used_ocr = models.BooleanField(default=False)
    answered_questions = models.PositiveSmallIntegerField(default=0)
    city = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Assessment log"
        verbose_name_plural = "Assessment logs"

    def __str__(self):
        label = self.predicted_disease or self.red_flag or "unknown"
        return f"{label} @ {self.created_at:%d %b %H:%M}"

    def symptom_count(self):
        return len([s for s in self.symptoms.split(",") if s.strip()])
