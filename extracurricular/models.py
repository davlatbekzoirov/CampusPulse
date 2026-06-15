import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Skill(models.Model):
    """A reusable soft-skill tag (Public Speaking, Budgeting, etc.)."""

    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Club(models.Model):
    """A club / society the student is (or was) part of."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clubs",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    skills = models.ManyToManyField(
        Skill, blank=True, related_name="clubs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("extracurricular:club_detail", args=[self.pk])

    @property
    def current_role(self):
        return self.roles.order_by("-start_date").first()


class ClubRole(models.Model):
    """A role held within a club over a date range (role progression)."""

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="roles")
    title = models.CharField(max_length=100) 
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} @ {self.club.name}"

    @property
    def is_current(self):
        return self.end_date is None or self.end_date >= timezone.localdate()


class VolunteerCause(models.Model):
    """Category used to group volunteer hours (Environment, Tutoring, etc.)."""

    name = models.CharField(max_length=60, unique=True)
    color = models.CharField(
        max_length=7,
        default="#4f46e5",
        help_text="Hex color used for the Chart.js doughnut chart.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VolunteerEntry(models.Model):
    """A single logged block of volunteer service."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="volunteer_entries",
    )
    cause = models.ForeignKey(
        VolunteerCause,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )
    organization = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    supervisor_name = models.CharField(max_length=120, blank=True)
    supervisor_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "volunteer entries"

    def __str__(self):
        return f"{self.organization} ({self.hours}h on {self.date})"


MILESTONE_TIERS = [
    ("Bronze", 25),
    ("Silver", 50),
    ("Gold", 100),
    ("Platinum", 200),
]


class ImpactEntry(models.Model):
    """A real-time logged achievement for future resume/LinkedIn use."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="impact_entries",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="impact_entries",
    )
    date = models.DateField(default=timezone.localdate)
    description = models.CharField(
        max_length=255,
        help_text="What did you do? e.g. Organized a charity bake sale",
    )
    impact = models.CharField(
        max_length=255,
        blank=True,
        help_text="Quantitative impact, e.g. Raised $450, attracted 120+ attendees",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name_plural = "impact entries"

    def __str__(self):
        return self.description


class ExtracurricularEvent(models.Model):
    """A one-off event, workshop, lecture, or recurring club meeting."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="extra_events",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title


class CalendarFeedToken(models.Model):
    """One-per-user secret token used to build the extracurricular iCal URL."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="extracurricular_feed_token",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Feed token for {self.user}"
