from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm

def home(request):
    return render(request, 'auth/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        # TODO: Check password here
        if form.is_valid():
            form.save()

            messages.success(request, f'Your account has been created. You can log in now!')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'auth/register.html', context)