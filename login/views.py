from django.http import HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages

from social import models

def login_view(request):
    """Serves lagin.djhtml from /e/macid/ (url name: login_view)
    Parameters
    ----------
      request: (HttpRequest) - POST with username and password or an empty GET
    Returns
    -------
      out: (HttpResponse)
                   POST - authenticate, login and redirect user to social app
                   GET - render login.djhtml with an authentication form
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            request.session['numPosts'] = 1
            request.session['numPeople'] = 1
            request.session['failed'] = False
            return redirect('social:messages_view')
        else:
            request.session['failed'] = True

    form = AuthenticationForm(request.POST)
    failed = request.session.get('failed',False)
    context = { 'login_form' : form,
                'failed' : failed }

    return render(request,'login.djhtml',context)

def logout_view(request):
    """Redirects to login_view from /e/macid/logout/ (url name: logout_view)
    Parameters
    ----------
      request: (HttpRequest) - expected to be an empty get request
    Returns
    -------
      out: (HttpResponse) - perform User logout and redirects to login_view
    """
    # TODO Objective 4 and 9: reset sessions variables
    request.session['numPosts'] = 1
    request.session['numPeople'] = 1
    # logout user
    logout(request)

    return redirect('login:login_view')

def signup_view(request):
    """Serves signup.djhtml from /e/macid/signup (url name: signup_view)
    Parameters
    ----------
      request : (HttpRequest) - expected to be an empty get request
    Returns
    -------
      out : (HttpRepsonse) - renders signup.djhtml
    """
    # TODO Objective 1: implement signup view
    if request.method == 'POST':
        context = request.POST
        givenUsernameInView = context['givenUsername']
        givenPasswordInVIew = context['givenPassword']
        if not validPass(givenPasswordInVIew):
            return render(request, 'signup.djhtml')
        try:
            models.UserInfo.objects.create_user_info(username=givenUsernameInView, password=givenPasswordInVIew)
        except:
            return render(request, 'signup.djhtml')
        _user = authenticate(request, username=givenUsernameInView, password=givenPasswordInVIew)
        if _user is not None:
            login(request,_user)
            request.session['numPosts'] = 1
            request.session['numPeople'] = 1
            request.session['failed'] = False
            return redirect('social:messages_view')

    return render(request,'signup.djhtml')


def validPass(s):
    numCheck = False
    lenCheck = False
    spaceCheck = True
    if len(s) >= 8:
        lenCheck = True
    for i in s:
        if i == ' ':
            spaceCheck = False
        if i == '1' or i == '2' or i == '3' or i == '4' or i == '5' or i == '6' or i == '7' or i == '8' or i == '9' or i == '0':
            numCheck = True
    if lenCheck and spaceCheck and spaceCheck:
        return True
    return False