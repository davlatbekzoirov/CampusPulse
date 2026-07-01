from django import forms

from .models import (
    Club,
    ClubRole,
    ExtracurricularEvent,
    ImpactEntry,
    Skill,
    VolunteerEntry,
)


class ClubForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Club
        fields = ["name", "description", "is_active", "skills"]


class ClubRoleForm(forms.ModelForm):
    class Meta:
        model = ClubRole
        fields = ["title", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class VolunteerEntryForm(forms.ModelForm):
    class Meta:
        model = VolunteerEntry
        fields = [
            "cause",
            "organization",
            "location",
            "date",
            "hours",
            "supervisor_name",
            "supervisor_email",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ImpactEntryForm(forms.ModelForm):
    class Meta:
        model = ImpactEntry
        fields = ["club", "date", "description", "impact"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.TextInput(
                attrs={"placeholder": "What did you do? e.g. Organized a charity bake sale"}
            ),
            "impact": forms.TextInput(
                attrs={"placeholder": "What was the quantitative impact? e.g. Raised $450, 120+ attendees"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["club"].queryset = Club.objects.filter(user=user)
            self.fields["club"].required = False


class ExtracurricularEventForm(forms.ModelForm):
    class Meta:
        model = ExtracurricularEvent
        fields = ["club", "title", "description", "location", "start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["club"].queryset = Club.objects.filter(user=user)
            self.fields["club"].required = False
