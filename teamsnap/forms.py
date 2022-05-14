from django import forms
from .models import Team, Location, Opponent, Event, Member
from django.forms import modelformset_factory, formset_factory, inlineformset_factory

select_kwargs = {
    'attrs':{'class': 'form-control form-control-sm'}
}

text_input_kwargs = {
    'attrs':{"readonly": "readonly", 'class':'form-control form-control-sm'}
}

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'benchcoach_object')
        labels = {
            'benchcoach_object': 'BenchCoach Link',
        }
        widgets = {
            "benchcoach_object": forms.Select(**select_kwargs),
            "first_name": forms.TextInput(**text_input_kwargs),
            "last_name": forms.TextInput(**text_input_kwargs),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('formatted_title', 'start_date', 'benchcoach_object')
        labels ={
            'formatted_title':"Title",
            'benchcoach_object':'BenchCoach Link',
            'start_date':'Date/Time'
        }
        widgets = {
            "benchcoach_object": forms.Select(**select_kwargs),
            "formatted_title":forms.TextInput(**text_input_kwargs),
            "start_date": forms.DateTimeInput(**text_input_kwargs)
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', 'benchcoach_object')
        labels ={
            'benchcoach_object':'BenchCoach Link',
        }
        widgets = {
            "name":forms.TextInput(**text_input_kwargs),
            "benchcoach_object": forms.Select(**select_kwargs)
        }

class OpponentForm(forms.ModelForm):
    class Meta:
        model = Opponent
        fields = ('name', 'benchcoach_object')
        labels ={
            'benchcoach_object':'BenchCoach Link',
        }
        widgets = {
            "name":forms.TextInput(**text_input_kwargs),
            "benchcoach_object": forms.Select(**select_kwargs)
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('name', 'benchcoach_object')
        labels ={
            'benchcoach_object':'BenchCoach Link',
        }
        widgets = {
            "name":forms.TextInput(**text_input_kwargs),
            "benchcoach_object": forms.Select(**select_kwargs)
        }

class LineupEntryForm(forms.Form):
    member = None
    availability = None
    lineup_entry = None

    event_lineup_entry_id = forms.Field(required=False)
    event_lineup_id = forms.Field(required=False)
    event_id = forms.Field()
    member_id = forms.Field()
    sequence = forms.IntegerField(required=False)
    label = forms.ChoiceField(required=False, choices=[
        ("--", "--"),
        ("P","P"),
        ("C","C"),
        ("1B","1B"),
        ("2B", "2B"),
        ("3B", "3B"),
        ("SS", "SS"),
        ('LF','LF'),
        ('CF','CF'),
        ('RF','RF'),
        ('DH','DH'),
        ('DR','DR'),
        ('EH','EH')
    ],
                              widget=forms.Select(
                                  attrs = {'onchange' : "colorPositions();"}
                              )
                              )


class EventChooseForm(forms.Form):
    event_id = forms.ChoiceField()

    # checked = forms.BooleanField(required=False)
    # def __init__(self, events, *args, **kwargs):
    #     super(EventChooseForm, self).__init__(*args, **kwargs)
    #     self.fields['foo'].choices = [e.data['id'] for e in events]

LineupEntryFormset = formset_factory(LineupEntryForm, can_delete=True, can_order=True, extra=0)


