from django.http import HttpResponse
from django.shortcuts import render,redirect, reverse, HttpResponseRedirect
from django.contrib.auth import login,authenticate

def welcome(request):
  pages = ['events list', 'teams list', 'venues list', 'players list', 'teamsnap list events', 'teamsnap home', 'login']
  return render(request,'home.html',{'pages':pages})


def user_login(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
      user = authenticate(request, username=username, password=password)
      if user is not None:
        print('Login')
        login(request,user)
        return redirect(reverse('home'))
      else:
        print("Someone tried to login and failed.")
        print("They used username: {} and password: {}".format(username, password))

        return redirect('/')
    except Exception as identifier:

      return redirect('/')

  else:
    return render(request, 'login.html')