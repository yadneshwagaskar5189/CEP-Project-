from django.db import models
from django.urls import reverse


class Scheme(models.Model):
    """A government healthcare scheme citizens can apply for."""

    LEVEL_CHOICES = [
        ("central", "Central Government"),
        ("state", "State Government (Maharashtra)"),
    ]

    CATEGORY_CHOICES = [
        ("insurance", "Health Insurance & Treatment Cover"),
        ("maternal", "Mothers & Newborns"),
        ("child", "Children & Adolescents"),
        ("senior", "Senior Citizens"),
        ("disease", "Specific Disease Programmes"),
        ("medicine", "Affordable Medicines & Diagnostics"),
        ("digital", "Digital Health Records"),
    ]

    # Which Maharashtra ration card colours make a family eligible.
    CARD_CHOICES = [
        ("yellow", "Yellow / Antyodaya card"),
        ("orange", "Orange card"),
        ("white", "White card"),
        ("any", "Any citizen"),
        ("senior70", "Age 70 and above"),
    ]

    name = models.CharField(max_length=200)
    short_name = models.CharField(
        max_length=60, blank=True, help_text="Common abbreviation, e.g. PM-JAY"
    )
    slug = models.SlugField(max_length=220, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="central")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="insurance")

    headline_benefit = models.CharField(
        max_length=200, help_text="One line, e.g. 'Rs 5 lakh cashless treatment per family per year'"
    )
    description = models.TextField()

    eligibility = models.TextField(help_text="One condition per line.")
    documents = models.TextField(help_text="One document per line.")
    application_steps = models.TextField(help_text="One step per line, in order.")

    eligible_cards = models.CharField(
        max_length=20, choices=CARD_CHOICES, default="any",
        help_text="Primary ration card category this scheme is aimed at.",
    )

    where_to_apply = models.CharField(max_length=250, blank=True)
    official_link = models.URLField(blank=True)
    helpline = models.CharField(max_length=60, blank=True)

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=100)
    last_verified = models.DateField(
        help_text="Date the details were last checked against the official source."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.short_name or self.name

    def get_absolute_url(self):
        return reverse("schemes:detail", args=[self.slug])

    # -- helpers used by templates -----------------------------------------
    def eligibility_list(self):
        return [line.strip() for line in self.eligibility.splitlines() if line.strip()]

    def document_list(self):
        return [line.strip() for line in self.documents.splitlines() if line.strip()]

    def step_list(self):
        return [line.strip() for line in self.application_steps.splitlines() if line.strip()]
