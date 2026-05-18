from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html', {'user': request.user})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print("Ошибки формы:", form.errors)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:product_list')  # или другая страница
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:product_list')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('store:product_list')