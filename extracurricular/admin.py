from django.contrib import admin

from .models import (
    CalendarFeedToken,
    Club,
    ClubRole,
    ExtracurricularEvent,
    ImpactEntry,
    Skill,
    VolunteerCause,
    VolunteerEntry,
)


class ClubRoleInline(admin.TabularInline):
    model = ClubRole
    extra = 1


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_active", "current_role")
    list_filter = ("is_active",)
    search_fields = ("name", "user__username", "user__email")
    filter_horizontal = ("skills",)
    inlines = [ClubRoleInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(VolunteerCause)
class VolunteerCauseAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


@admin.register(VolunteerEntry)
class VolunteerEntryAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "cause", "date", "hours")
    list_filter = ("cause", "date")
    search_fields = ("organization", "location", "user__username")
    date_hierarchy = "date"


@admin.register(ImpactEntry)
class ImpactEntryAdmin(admin.ModelAdmin):
    list_display = ("description", "user", "club", "date")
    list_filter = ("club", "date")
    search_fields = ("description", "impact", "user__username")
    date_hierarchy = "date"


@admin.register(ExtracurricularEvent)
class ExtracurricularEventAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "club", "start_time", "end_time")
    list_filter = ("club",)
    search_fields = ("title", "user__username")
    date_hierarchy = "start_time"


@admin.register(CalendarFeedToken)
class CalendarFeedTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")
    readonly_fields = ("token",)
