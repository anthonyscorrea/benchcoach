from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.base import TemplateView
from django.forms.models import model_to_dict
from django import forms
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
# from .models import Event
# from .forms import EventForm
from django.http import HttpResponse


class BenchcoachListView(TemplateView):
    Model = models.Model
    template_name = 'list.html'
    edit_url = 'edit item'
    list_url = 'items list'
    template_name = 'list.html'
    page_title = f"{Model.__name__}s"
    title_strf = "{item}"
    subtitle_strf = ""
    body_strf = ""

    def get_context_data(self):
        items = self.Model.objects.all()
        context = {
            'title': self.page_title,
            'items': [
                {
                    'id': item.id,
                    'title': self.title_strf.format(item=item, **model_to_dict(item)),
                    'subtitle': self.subtitle_strf.format(item=item, **model_to_dict(item)),
                    'body': self.body_strf.format(item=item, **model_to_dict(item)),
                    'buttons': [
                        {
                            'label': 'Edit',
                            'href': reverse(self.edit_url, args=[item.id])
                        }
                    ]
                }
                for item in items
            ]
        }
        return context

class BenchcoachEditView(TemplateView):
    Form: forms.ModelForm = None
    Model: models.Model = None
    edit_url = 'edit item'
    list_url = 'items list'

    def post(self, request, *args, **kwargs):
        id = kwargs.get('id')
        # create a form instance and populate it with data from the request:
        if id:
            instance = get_object_or_404(self.Model, id=id)
            form = self.Form(request.POST or None, instance=instance)
        else:
            form = self.Form(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_item, did_create = self.Model.objects.update_or_create(pk=id, defaults=form.cleaned_data)
            return render(request, 'success.html', {'call_back_url': reverse(self.list_url), 'id': new_item.id},
                          status=201 if did_create else 200)
        return HttpResponseBadRequest()

    def get(self, request, *args, **kwargs):
        pass
        id = kwargs.get('id')
        if id:
            instance = get_object_or_404(self.Model, id=id)
            form = self.Form(request.POST or None, instance=instance)
        else:
            form = self.Form
        return render(request, 'edit.html', {'form': form, 'id': id, 'call_back': self.edit_url})
