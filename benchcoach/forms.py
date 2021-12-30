from django import forms
from .models import Event, Positioning, Team, Venue, Player
from teamsnap.models import Event as TeamsnapEvent
from django.forms import modelformset_factory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['start', 'home_team', 'away_team', 'venue']
class PositioningForm(forms.ModelForm):
    availability = None
    class Meta:
        model = Positioning
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control form-control-sm', 'onchange':'positionSelectChanged(this)'})
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

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'jersey_number', 'team']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name']