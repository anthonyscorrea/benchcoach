from django import forms
from .models import LineupEntry
from events.models import Event
from players.models import Player
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet,formset_factory
from crispy_forms.helper import FormHelper, Layout

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
