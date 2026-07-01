"""
Hook for the existing Celery-driven Monday Morning Email Digest.

Wherever your digest task builds its context/email body, import and call
`get_extracurricular_digest_section(user)` and append the returned string
(or dict, if your digest template expects structured context) to the email.

Example integration in your existing digest task:

    from extracurricular.tasks import get_extracurricular_digest_section

    @shared_task
    def send_monday_digest(user_id):
        user = User.objects.get(pk=user_id)
        sections = [...]  # existing digest sections
        sections.append(get_extracurricular_digest_section(user))
        ...
"""

from django.utils import timezone

from .models import VolunteerEntry, ExtracurricularEvent, MILESTONE_TIERS
from django.db.models import Sum


def get_extracurricular_digest_section(user):
    """Return a plain-text summary for this week's extracurricular digest."""

    now = timezone.now()
    week_end = now + timezone.timedelta(days=7)

    upcoming_events = ExtracurricularEvent.objects.filter(
        user=user, start_time__gte=now, start_time__lt=week_end
    )
    event_count = upcoming_events.count()

    total_hours = (
        VolunteerEntry.objects.filter(user=user).aggregate(total=Sum("hours"))["total"] or 0
    )

    # Find the next unmet milestone.
    next_tier = None
    for name, threshold in MILESTONE_TIERS:
        if total_hours < threshold:
            next_tier = (name, threshold)
            break

    lines = []
    if event_count:
        plural = "meeting" if event_count == 1 else "meetings/events"
        lines.append(f"This week you have {event_count} club {plural}.")
    else:
        lines.append("No club meetings or events scheduled this week.")

    if next_tier:
        remaining = next_tier[1] - total_hours
        lines.append(
            f"You are {remaining} hours away from your {next_tier[0]} Volunteer Milestone!"
        )
    else:
        lines.append("You've reached the Platinum Volunteer Milestone — amazing work!")

    return " ".join(lines)
