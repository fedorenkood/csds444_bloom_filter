from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import UserRegistrationForm, CustomUserDataForm
from .forms import PasswordResetForm


def home(request):
    return render(request, 'auth/home.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        custom_data_form = CustomUserDataForm(request.POST)
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        # TODO: Check password here
        if user_form.is_valid() and custom_data_form.is_valid():
            u = user_form.save()
            custom_data_form = CustomUserDataForm(request.POST, instance=u.customuserdata)
            custom_data_form.save()

            messages.success(request, f'Your account has been created. You can log in now!')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        custom_data_form = CustomUserDataForm()

    context = {'user_form': user_form, 'custom_data_form': custom_data_form}
    return render(request, 'auth/register.html', context)


def password_reset(request):
    if request.method == 'POST':
        user_password_form = PasswordResetForm(user=None, data=request.POST)
        custom_data_form = CustomUserDataForm(data=request.POST)
        if user_password_form.is_valid() and custom_data_form.is_valid():
            # Fetch user from claimed email:
            user = User.objects.get(email__exact=user_password_form.cleaned_data['email'])
            # Check if challenge question responses were correct:
            if custom_data_form.matches_challenge_questions(user.customuserdata):
                # Save user's new password:
                user_password_form = PasswordResetForm(user=user, data=request.POST)
                if user_password_form.is_valid():
                    user_password_form.save()
                    messages.success(request, f'Your password has been reset.')
                    return redirect('login')
            else:
                custom_data_form.add_error(None, "Failed challenge questions :((((((((((((((((((((((((((((((((((")
                context = {'user_password_form': user_password_form, 'custom_data_form': custom_data_form}
                return render(request, 'auth/password-reset.html', context)
    else:
        user_password_form = PasswordResetForm(user=None)
        custom_data_form = CustomUserDataForm()

    context = {'user_password_form': user_password_form, 'custom_data_form': custom_data_form}
    return render(request, 'auth/password-reset.html', context)
