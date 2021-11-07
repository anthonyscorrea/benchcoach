from django.http import HttpResponse
from django.shortcuts import render

def welcome(request):
  pages = ['schedule', 'teams_list', 'venues_list']
  return render(request,'home.html',{'pages':pages})