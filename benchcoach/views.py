from django.http import HttpResponse
from django.shortcuts import render

def welcome(request):
  pages = ['schedule', 'teams list', 'venues list', 'players list']
  return render(request,'home.html',{'pages':pages})