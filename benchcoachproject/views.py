from django.http import HttpResponse
from django.shortcuts import render,redirect, reverse, HttpResponseRedirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

@login_required()
def welcome(request):
  pages = ['event list', 'team list', 'venue list', 'player list', 'teamsnap home', 'login_view']
  return render(request,'home.html',{'pages':pages})

def logout_benchcoachproject(request):
  if request.method == "POST":
    logout(request)
  return redirect('home')

def login_view(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect(reverse('home'))
      else:
        print("Someone tried to login_view and failed.")
        print("They used username: {} and password: {}".format(username, password))

        return redirect('/')
    except Exception as identifier:

      return redirect('/')

  else:
    return render(request, 'login.html')