from django import forms
from .models import Team, Location, Opponent, Event, Member
from django.forms import modelformset_factory

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


