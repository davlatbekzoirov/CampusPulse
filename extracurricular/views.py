import uuid
from datetime import timedelta, timezone as dt_timezone

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    ClubForm,
    ClubRoleForm,
    ExtracurricularEventForm,
    ImpactEntryForm,
    VolunteerEntryForm,
)
from .models import (
    CalendarFeedToken,
    Club,
    ClubRole,
    ExtracurricularEvent,
    ImpactEntry,
    MILESTONE_TIERS,
    VolunteerEntry,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def get_volunteer_summary(user):
    """Total hours, cause breakdown, and milestone progress for a user."""
    entries = VolunteerEntry.objects.filter(user=user)
    total_hours = entries.aggregate(total=Sum("hours"))["total"] or 0

    by_cause = (
        entries.values("cause__name", "cause__color")
        .annotate(total=Sum("hours"))
        .order_by("-total")
    )

    # Determine current/next milestone tier.
    current_tier = None
    next_tier = None
    for name, threshold in MILESTONE_TIERS:
        if total_hours >= threshold:
            current_tier = (name, threshold)
        elif next_tier is None:
            next_tier = (name, threshold)

    if next_tier:
        prev_threshold = current_tier[1] if current_tier else 0
        span = next_tier[1] - prev_threshold
        progress_pct = min(
            100, round(((total_hours - prev_threshold) / span) * 100, 1)
        ) if span else 100
        hours_remaining = max(0, next_tier[1] - total_hours)
    else:
        progress_pct = 100
        hours_remaining = 0

    return {
        "total_hours": total_hours,
        "by_cause": list(by_cause),
        "current_tier": current_tier,
        "next_tier": next_tier,
        "progress_pct": progress_pct,
        "hours_remaining": hours_remaining,
        "tiers": MILESTONE_TIERS,
    }


def get_or_create_feed_token(user):
    token, _ = CalendarFeedToken.objects.get_or_create(user=user)
    return token


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    user = request.user

    total_clubs = Club.objects.filter(user=user, is_active=True).count()
    volunteer_summary = get_volunteer_summary(user)
    total_impacts = ImpactEntry.objects.filter(user=user).count()

    next_event = (
        ExtracurricularEvent.objects.filter(
            user=user, start_time__gte=timezone.now()
        )
        .order_by("start_time")
        .first()
    )

    recent_impacts = ImpactEntry.objects.filter(user=user)[:5]

    context = {
        "total_clubs": total_clubs,
        "volunteer_summary": volunteer_summary,
        "total_impacts": total_impacts,
        "next_event": next_event,
        "recent_impacts": recent_impacts,
        "feed_token": get_or_create_feed_token(user).token,
    }
    return render(request, "extracurricular/dashboard.html", context)


# ---------------------------------------------------------------------------
# 1. Club & Society Role Ledger
# ---------------------------------------------------------------------------

@login_required
def club_list(request):
    clubs = (
        Club.objects.filter(user=request.user)
        .prefetch_related("roles", "skills")
    )

    # Build a soft-skill tag cloud across all clubs.
    skill_counts = {}
    for club in clubs:
        for skill in club.skills.all():
            skill_counts[skill.name] = skill_counts.get(skill.name, 0) + 1
    tag_cloud = sorted(skill_counts.items(), key=lambda x: -x[1])

    return render(
        request,
        "extracurricular/club_list.html",
        {"clubs": clubs, "tag_cloud": tag_cloud},
    )


@login_required
def club_create(request):
    if request.method == "POST":
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.user = request.user
            club.save()
            form.save_m2m()
            return redirect("extracurricular:club_detail", pk=club.pk)
    else:
        form = ClubForm()
    return render(request, "extracurricular/club_form.html", {"form": form})


@login_required
def club_detail(request, pk):
    club = get_object_or_404(Club, pk=pk, user=request.user)
    role_form = ClubRoleForm()
    return render(
        request,
        "extracurricular/club_detail.html",
        {"club": club, "role_form": role_form},
    )


@login_required
def club_edit(request, pk):
    club = get_object_or_404(Club, pk=pk, user=request.user)
    if request.method == "POST":
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            form.save()
            return redirect("extracurricular:club_detail", pk=club.pk)
    else:
        form = ClubForm(instance=club, initial={"skills": club.skills.all()})
    return render(
        request, "extracurricular/club_form.html", {"form": form, "club": club}
    )


@login_required
def club_delete(request, pk):
    club = get_object_or_404(Club, pk=pk, user=request.user)
    if request.method == "POST":
        club.delete()
        return redirect("extracurricular:club_list")
    return render(request, "extracurricular/confirm_delete.html", {"object": club})


@login_required
def club_role_add(request, pk):
    club = get_object_or_404(Club, pk=pk, user=request.user)
    if request.method == "POST":
        form = ClubRoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.club = club
            role.save()
    return redirect("extracurricular:club_detail", pk=club.pk)


@login_required
def club_role_delete(request, pk, role_pk):
    club = get_object_or_404(Club, pk=pk, user=request.user)
    role = get_object_or_404(ClubRole, pk=role_pk, club=club)
    if request.method == "POST":
        role.delete()
    return redirect("extracurricular:club_detail", pk=club.pk)


# ---------------------------------------------------------------------------
# 2. Volunteer Hour Log & Milestone Tracker
# ---------------------------------------------------------------------------

@login_required
def volunteer_list(request):
    entries = VolunteerEntry.objects.filter(user=request.user).select_related("cause")
    summary = get_volunteer_summary(request.user)
    return render(
        request,
        "extracurricular/volunteer_list.html",
        {"entries": entries, "summary": summary},
    )


@login_required
def volunteer_create(request):
    if request.method == "POST":
        form = VolunteerEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("extracurricular:volunteer_list")
    else:
        form = VolunteerEntryForm()
    return render(request, "extracurricular/volunteer_form.html", {"form": form})


@login_required
def volunteer_edit(request, pk):
    entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = VolunteerEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("extracurricular:volunteer_list")
    else:
        form = VolunteerEntryForm(instance=entry)
    return render(
        request, "extracurricular/volunteer_form.html", {"form": form, "entry": entry}
    )


@login_required
def volunteer_delete(request, pk):
    entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return redirect("extracurricular:volunteer_list")
    return render(request, "extracurricular/confirm_delete.html", {"object": entry})


# ---------------------------------------------------------------------------
# 3. Impact Journal
# ---------------------------------------------------------------------------

@login_required
def impact_list(request):
    entries = ImpactEntry.objects.filter(user=request.user).select_related("club")
    return render(request, "extracurricular/impact_list.html", {"entries": entries})


@login_required
def impact_create(request):
    if request.method == "POST":
        form = ImpactEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("extracurricular:impact_list")
    else:
        form = ImpactEntryForm(user=request.user)
    return render(request, "extracurricular/impact_form.html", {"form": form})


@login_required
def impact_edit(request, pk):
    entry = get_object_or_404(ImpactEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = ImpactEntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("extracurricular:impact_list")
    else:
        form = ImpactEntryForm(instance=entry, user=request.user)
    return render(
        request, "extracurricular/impact_form.html", {"form": form, "entry": entry}
    )


@login_required
def impact_delete(request, pk):
    entry = get_object_or_404(ImpactEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return redirect("extracurricular:impact_list")
    return render(request, "extracurricular/confirm_delete.html", {"object": entry})


# ---------------------------------------------------------------------------
# 4. Event & Workshop Calendar
# ---------------------------------------------------------------------------

@login_required
def event_list(request):
    events = ExtracurricularEvent.objects.filter(user=request.user).select_related("club")
    feed_token = get_or_create_feed_token(request.user).token
    feed_url = request.build_absolute_uri(
        reverse("extracurricular:ical_feed", args=[feed_token])
    )
    return render(
        request,
        "extracurricular/event_list.html",
        {"events": events, "feed_url": feed_url},
    )


@login_required
def event_create(request):
    if request.method == "POST":
        form = ExtracurricularEventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect("extracurricular:event_list")
    else:
        form = ExtracurricularEventForm(user=request.user)
    return render(request, "extracurricular/event_form.html", {"form": form})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(ExtracurricularEvent, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExtracurricularEventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("extracurricular:event_list")
    else:
        form = ExtracurricularEventForm(instance=event, user=request.user)
    return render(
        request, "extracurricular/event_form.html", {"form": form, "event": event}
    )


@login_required
def event_delete(request, pk):
    event = get_object_or_404(ExtracurricularEvent, pk=pk, user=request.user)
    if request.method == "POST":
        event.delete()
        return redirect("extracurricular:event_list")
    return render(request, "extracurricular/confirm_delete.html", {"object": event})


@login_required
def regenerate_feed_token(request):
    """Reset the user's iCal feed token (invalidates the old URL)."""
    if request.method == "POST":
        CalendarFeedToken.objects.filter(user=request.user).delete()
        CalendarFeedToken.objects.create(user=request.user, token=uuid.uuid4())
    return redirect("extracurricular:event_list")


# ---------------------------------------------------------------------------
# iCal feed (public via secret token, mirrors University Tracker logic)
# ---------------------------------------------------------------------------

def _format_ical_dt(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ical_feed(request, token):
    try:
        feed_token = CalendarFeedToken.objects.select_related("user").get(token=token)
    except (CalendarFeedToken.DoesNotExist, ValueError):
        raise Http404("Invalid calendar feed token")

    user = feed_token.user
    events = ExtracurricularEvent.objects.filter(user=user)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CampusLife//Extracurricular Calendar//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Extracurricular Activities",
    ]

    now_stamp = _format_ical_dt(timezone.now())

    for event in events:
        end_time = event.end_time or (event.start_time + timedelta(hours=1))
        lines += [
            "BEGIN:VEVENT",
            f"UID:extracurricular-{event.pk}@campuslife",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART:{_format_ical_dt(event.start_time)}",
            f"DTEND:{_format_ical_dt(end_time)}",
            f"SUMMARY:{event.title}",
        ]
        if event.location:
            lines.append(f"LOCATION:{event.location}")
        if event.description:
            description = event.description.replace("\n", "\\n")
            lines.append(f"DESCRIPTION:{description}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    response = HttpResponse("\r\n".join(lines), content_type="text/calendar")
    response["Content-Disposition"] = 'attachment; filename="extracurricular.ics"'
    return response
