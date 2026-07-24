from django.db import models
from django.utils import timezone


class Specialisation(models.Model):
    """A department a hospital offers, e.g. Cardiology."""

    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Hospital(models.Model):
    TYPE_CHOICES = [
        ("govt", "Government"),
        ("municipal", "Municipal / Civic"),
        ("trust", "Trust / Charitable"),
        ("private", "Private"),
    ]

    name = models.CharField(max_length=200)
    hospital_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="private")
    address = models.CharField(max_length=300)
    area = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, db_index=True)
    district = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    contact_number = models.CharField(max_length=40, blank=True)
    emergency_number = models.CharField(max_length=40, blank=True)

    specialisations = models.ManyToManyField(Specialisation, blank=True, related_name="hospitals")

    has_emergency = models.BooleanField(default=True, verbose_name="24x7 emergency")
    has_ambulance = models.BooleanField(default=False)
    accepts_pmjay = models.BooleanField(
        default=False, verbose_name="Empanelled for PM-JAY / MJPJAY"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name}, {self.city}"

    @property
    def beds(self):
        """Latest bed record, or None."""
        return self.bed_records.first()


class BedAvailability(models.Model):
    """
    Bed counts for a hospital.

    NOTE FOR THE PROJECT REPORT: India has no public real-time API for hospital
    bed occupancy. This table is updated manually through the Django admin,
    which simulates the data feed a hospital would push in a live deployment.
    Every page that shows these numbers states when they were last updated.
    """

    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="bed_records"
    )

    total_beds = models.PositiveIntegerField(default=0)
    general_available = models.PositiveIntegerField(default=0, verbose_name="General beds free")
    icu_available = models.PositiveIntegerField(default=0, verbose_name="ICU beds free")
    oxygen_available = models.PositiveIntegerField(default=0, verbose_name="Oxygen beds free")
    ventilator_available = models.PositiveIntegerField(default=0, verbose_name="Ventilators free")

    updated_by = models.CharField(max_length=80, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]
        verbose_name = "Bed availability record"
        verbose_name_plural = "Bed availability records"

    def __str__(self):
        return f"{self.hospital.name} - {self.total_free} free"

    # -- derived values -----------------------------------------------------
    @property
    def total_free(self):
        return (
            self.general_available
            + self.icu_available
            + self.oxygen_available
            + self.ventilator_available
        )

    @property
    def occupancy_percent(self):
        if not self.total_beds:
            return 0
        return round(100 * (1 - self.total_free / self.total_beds))

    @property
    def free_percent(self):
        if not self.total_beds:
            return 0
        return round(100 * self.total_free / self.total_beds)

    @property
    def status(self):
        """Drives the colour band in the UI: open / limited / full."""
        pct = self.free_percent
        if pct >= 20:
            return "open"
        if pct >= 10:
            return "limited"
        return "full"

    @property
    def status_label(self):
        return {"open": "Beds available", "limited": "Filling up", "full": "Almost full"}[self.status]

    @property
    def is_stale(self):
        """True if nobody has updated this in over 24 hours."""
        return (timezone.now() - self.last_updated).total_seconds() > 86400
