from django import forms
from .models import Positioning
from events.models import Event
from players.models import Player
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet,formset_factory
from crispy_forms.helper import FormHelper, Layout
from teamsnap.models import Event as TeamsnapEvent

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

class TeamsnapEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeamsnapEventForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.teamsnap_event.first():
            initial = (self.instance.teamsnap_event.first().id, self.instance.teamsnap_event.first())
        else:
            initial = None
        self.fields = {}
        choices = [("","-----")]
        choices += [(choice.id, choice) for choice in TeamsnapEvent.objects.all()]
        self.fields['teamsnap event'] = forms.MultipleChoiceField(
            widget=forms.Select(attrs={'class': 'form-control'}),
            choices=choices,
            initial=initial
        )

    class Meta:
        model = Event
        fields = ['start', 'home_team', 'away_team', 'venue']