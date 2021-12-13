from django.http import HttpResponse
from django.shortcuts import render

def welcome(request):
  pages = ['events list', 'teams list', 'venues list', 'players list', 'teamsnap list events', 'teamsnap home']
  return render(request,'home.html',{'pages':pages})