from django.db import models


class HealthTip(models.Model):
    """Short awareness cards shown on the home page."""

    title = models.CharField(max_length=140)
    body = models.TextField()
    icon = models.CharField(
        max_length=20, default="drop",
        help_text="One of: drop, lungs, heart, shield, plate, sun",
    )
    display_order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title
