from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meet
from .forms import MeetForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        form = MeetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meet = form.save(commit=False)
                meet.user = request.user
                meet.save()
                messages.success(request, ("Seu Meet Foi Postado com Sucesso"))
                return redirect('home')
        meets = Meet.objects.all().order_by("-create_at")
        return render(request, 'home.html', {"meets":meets, "form":form})
    else:
        meets = Meet.objects.all().order_by("-create_at")
        return render(request, 'home.html', {"meets":meets})

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles":profiles})
    else:
        messages.success(request, ("Voce nao esta logado..."))
        return redirect('home')

def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meets = Meet.objects.filter(user_id=pk)

        if request.method=="POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
                current_user_profile.save()



        return render(request, 'profile.html', {"profile":profile, "meets":meets})
    else:
        messages.success(request, ("Voce nao esta logado..."))
        return redirect('home')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("Esta Logado "))
            return redirect('home')
        else:
            messages.success(request, ("Sua Senha ou Nome de Usuario esta incorreta.Por favor tente outra vez!"))
            return redirect('login')

    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Voce Saiu!"))
    return redirect('login')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            # logar o usuario
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Sua conta foi registada com sucesso!"))
            return redirect('home')
    return render(request, 'register.html', {'form':form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            login(request, current_user)
            messages.success(request, ('Conta actualizada'))
            return redirect('home')

        return render(request, 'update_user.html', {'user_form':user_form, 'profile_form':profile_form})
    else:
        messages.success(request, ('Voce nao esta logado!'))
        return redirect('home')

def meet_like(request, pk):
    if request.user.is_authenticated:
        meet = get_object_or_404(Meet, id=pk)
        if meet.likes.filter(id=request.user.id):
            meet.likes.remove(request.user)
        else:
            meet.likes.add(request.user)
            return redirect('home')

    else:
        messages.success(request, ('Voce nao esta logado!'))
        return redirect('home')
