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
            # 'order': forms.NumberInput(attrs={'class':'w-100'}),
            # 'player': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            # 'ordering': forms.NumberInput(attrs={'class':'w-100'})
        }
        exclude = ()

PositioningFormSet = modelformset_factory(
    model=Positioning,
    form=PositioningForm,
    # fields=['order', 'position','player'],
    # min_num=9,
    extra=0

)

# class PositioningFormSet(modelformset_factory):
#     class Meta:
#         model = Positioning
#         fields = ['player', 'position', 'order']
#         widgets = {
#             'order':forms.NumberInput(attrs={'style':'width:6ch'})
#         }
