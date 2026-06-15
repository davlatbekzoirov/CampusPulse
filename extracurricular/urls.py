from django.urls import path

from . import views

app_name = "extracurricular"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("clubs/", views.club_list, name="club_list"),
    path("clubs/new/", views.club_create, name="club_create"),
    path("clubs/<int:pk>/", views.club_detail, name="club_detail"),
    path("clubs/<int:pk>/edit/", views.club_edit, name="club_edit"),
    path("clubs/<int:pk>/delete/", views.club_delete, name="club_delete"),
    path("clubs/<int:pk>/roles/add/", views.club_role_add, name="club_role_add"),
    path(
        "clubs/<int:pk>/roles/<int:role_pk>/delete/",
        views.club_role_delete,
        name="club_role_delete",
    ),

    path("volunteering/", views.volunteer_list, name="volunteer_list"),
    path("volunteering/new/", views.volunteer_create, name="volunteer_create"),
    path("volunteering/<int:pk>/edit/", views.volunteer_edit, name="volunteer_edit"),
    path("volunteering/<int:pk>/delete/", views.volunteer_delete, name="volunteer_delete"),

    path("impact/", views.impact_list, name="impact_list"),
    path("impact/resume-generator/", views.resume_generator, name="resume_generator"),
    path("impact/new/", views.impact_create, name="impact_create"),
    path("impact/<int:pk>/edit/", views.impact_edit, name="impact_edit"),
    path("impact/<int:pk>/delete/", views.impact_delete, name="impact_delete"),

    path("events/", views.event_list, name="event_list"),
    path("events/new/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("events/feed/regenerate/", views.regenerate_feed_token, name="regenerate_feed_token"),
    path("events/feed/<uuid:token>.ics", views.ical_feed, name="ical_feed"),

    path("portfolio/settings/", views.portfolio_settings, name="portfolio_settings"),
    path("portfolio/<str:username>/", views.public_portfolio, name="public_portfolio"),

    path("analytics/insights/", views.analytics_insights, name="analytics_insights"),
]
