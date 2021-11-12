from django import forms
from .models import Positioning
from events.models import Event
from players.models import Player
from django.forms import modelformset_factory, inlineformset_factory, NumberInput
from crispy_forms.helper import FormHelper, Layout

class PositioningForm(forms.ModelForm):
    class Meta:
        model = Positioning
        widgets = {
            'order': forms.NumberInput(attrs={'class':'input-group-text w-25'}),
            'player': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'input-group-text w-25'})
        }
        exclude = ()

PositioningFormSet = modelformset_factory(
    model=Positioning,
    form=PositioningForm,
    fields = ['player', 'position', 'order'],
    min_num=9
)

# class PositioningFormSet(modelformset_factory):
#     class Meta:
#         model = Positioning
#         fields = ['player', 'position', 'order']
#         widgets = {
#             'order':forms.NumberInput(attrs={'style':'width:6ch'})
#         }
