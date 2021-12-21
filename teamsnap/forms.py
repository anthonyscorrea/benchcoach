from django import forms
from .models import LineupEntry, Event
from players.models import Player
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet,formset_factory

class LineupEntryForm(forms.ModelForm):
    availability = None
    class Meta:
        model = LineupEntry
        widgets = {
            'label': forms.Select(attrs={'class': 'form-control form-control-sm'})
        }
        exclude = ()

LineupEntryFormSet = modelformset_factory(
    model=LineupEntry,
    form=LineupEntryForm,
    extra=0
)

class EventForm(forms.ModelForm):
    availability = None
    class Meta:
        model = Event
        fields = ('formatted_title', 'start_date', 'benchcoach_object')
        labels ={
            'formatted_title':"Title",
            'benchcoach_object':'BenchCoach Link',
            'start_date':'Date/Time'
        }
        widgets = {
            "formatted_title":forms.TextInput(attrs={"disabled":"disabled"}),
            "start_date": forms.DateTimeInput(attrs={"disabled": "disabled"})
        }

EventFormSet = modelformset_factory(
    model=Event,
    form=EventForm,
    extra=0
)
