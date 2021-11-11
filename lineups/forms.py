from django import forms
from .models import Positioning
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper, Layout

PositioningFormSet = modelformset_factory(model=Positioning,
        fields = ['player', 'position', 'order'],
        widgets = {
            'order':forms.NumberInput(attrs={'style':'width:6ch'})
        })

# class PositioningFormSet(modelformset_factory):
#     class Meta:
#         model = Positioning
#         fields = ['player', 'position', 'order']
#         widgets = {
#             'order':forms.NumberInput(attrs={'style':'width:6ch'})
#         }
