from django import forms
from .models import Positioning
from events.models import Event
from players.models import Player
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet,formset_factory
from crispy_forms.helper import FormHelper, Layout

class PositioningForm(forms.ModelForm):
    availability = None
    class Meta:
        model = Positioning
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control form-control-sm'})
        }
        exclude = ()

PositioningFormSet = modelformset_factory(
    model=Positioning,
    form=PositioningForm,
    # fields=['order', 'position','player'],
    # min_num=9,
    extra=0

)
