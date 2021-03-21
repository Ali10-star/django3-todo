# imports...
from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request) :
    return render(request, 'todo/home.html')

def signupuser( request ) :
    if request.method == 'GET' :
        return render(request, 'todo/signupuser.html', { 'form' : UserCreationForm() } )
    else :
        #? Create a new user
        if request.POST['password1'] == request.POST['password2'] :
            try :
                user = User.objects.create_user( request.POST['username'], password = request.POST['password1'] )
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError :
                return render(request, 'todo/signupuser.html', { 'form' : UserCreationForm(), 'error' : 'Username already exists, please choose another one' } )

        else :
            return render(request, 'todo/signupuser.html', { 'form' : UserCreationForm(), 'error' : 'Passwords did not match, try again ! ' } )

def loginuser(request) :
        if request.method == 'GET' :
            return render(request, 'todo/loginuser.html', { 'form' : AuthenticationForm() } )
        else :
            user = authenticate(request, username = request.POST['username'],  password = request.POST['password'])
            if user == None : # failed login
                return render(request, 'todo/loginuser.html', { 'form' : AuthenticationForm(), 'error' : 'Wrong username or password, try again.' } )
            else : # successfull login
                login(request, user)
                return redirect('currenttodos')

@login_required
def logoutuser(request) :
    if request.method == 'POST' : #! what happens when user presses "logout" button
        logout(request)
        return redirect('home')

@login_required
def currenttodos(request) :
    #? Filter todos so it matches the authenticated user only and is not completed
    todos = Todo.objects.filter( user = request.user, datecompleted__isnull = True )
    return render( request, 'todo/currenttodos.html', { 'todos' : todos } )

@login_required
def createtodo(request) :
    if request.method == 'GET' :  #! user pressed the "create todo" button
        return render(request, 'todo/createtodo.html', { 'form' : TodoForm() } )
    else :  #! actual process of creating an object and storing it in the DB
        try :
            form = TodoForm(request.POST)
            newTodo = form.save(commit = False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('currenttodos')
        except ValueError :
            return render(request, 'todo/createtodo.html', { 'form' : TodoForm(), 'error' : 'Bad data passed in'} )

@login_required
def viewtodo(request, todo_pk ) :
    todo = get_object_or_404( Todo, pk = todo_pk, user = request.user )

    if request.method == 'GET' :
        form = TodoForm( instance = todo )
        return render( request, 'todo/viewtodo.html', { 'todo' : todo , 'form' : form } )
    else :
        try :
            form = TodoForm(request.POST, instance = todo )
            form.save()
            return redirect('currenttodos')
        except ValueError :
            return render(request, 'todo/viewtodo.html', { 'todo' : todo  , 'form' : form, 'error' : 'Bad data passed in'} )


@login_required
def completetodo( request, todo_pk ) :
    todo = get_object_or_404( Todo, pk = todo_pk, user = request.user )
    if request.method == 'POST' :
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo( request, todo_pk ) :
    todo = get_object_or_404( Todo, pk = todo_pk, user = request.user )
    if request.method == 'POST' :
        todo.delete()
        return redirect('currenttodos')

@login_required
def completedtodos(request) :
    #? Filter todos so it matches the authenticated user only and is completed
    todos = Todo.objects.filter( user = request.user, datecompleted__isnull = False ).order_by('-datecompleted')
    return render( request, 'todo/completedtodos.html', { 'todos' : todos } )