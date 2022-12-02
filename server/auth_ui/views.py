import base64
from io import BytesIO

import pyotp
import qrcode
from django.contrib import messages
from django.contrib.auth import login as django_auth_login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import PasswordResetForm, EmailPasswordResetForm
from .forms import UserRegistrationForm, ChallengeQuestionsRegisterForm, ChallengeQuestionsResetForm, User2faValidationForm, UserLoginForm

def home(request):
    return render(request, 'auth/home.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        challenge_questions_form = ChallengeQuestionsRegisterForm(request.POST)
        if user_form.is_valid() and user_form.validate(request) and challenge_questions_form.is_valid():
            return __register_2fa(request, user_form, challenge_questions_form)
    else:
        user_form = UserRegistrationForm()
        challenge_questions_form = ChallengeQuestionsRegisterForm()
    context = {'user_form': user_form, 'challenge_questions_form': challenge_questions_form}
    return render(request, 'auth/register.html', context)


def __register_2fa(request, user_form, challenge_questions_form):
    """View for the 2FA registration step, entailing QR code presentation for the TOTP Secret, as well as validation
    of the user being able to generate validation codes on their phone. Note that 2FA validation is also done here,
    because we want to ensure that the user can actually use 2FA on their new account before we expect them to use
    2FA in future logins."""
    user_2fa_form = User2faValidationForm()
    if request.POST.get('step', None) == '2fa':
        # If the second step (2FA page) was posted, then validate and finish registering the account:
        user_2fa_form = User2faValidationForm(request.POST)
        otp_secret = request.POST.get('otp_secret', None)
        if user_2fa_form.is_valid() and otp_secret is not None:
            # Create the pyotp TOTP object for validating expected codes given the secret:
            totp = pyotp.totp.TOTP(otp_secret)
            # Get the user inputted TOTP validation code:
            user_inputted_code = user_2fa_form.cleaned_data['validation_code']
            if totp.verify(user_inputted_code):
                # Save to the basic user table, and acquire a CustomUserData reference:
                user = user_form.save()
                # Save challenge questions:
                ChallengeQuestionsRegisterForm(request.POST, instance=user.customuserdata).save(True)
                # Save OTP Secret for future 2FA logins:
                user.customuserdata.otp_secret = otp_secret
                # Commit the save in the db:
                user.customuserdata.save()
                # User account should now be finally registered:
                messages.success(request, f'Your account has been created. You can log in now!')
                return redirect('login')
            else:
                user_2fa_form.add_error('validation_code', 'Failed to authenticate: wrong code.')
    else:
        # If the first/initial registration step page was posted, then serve the second step (2FA setup):
        otp_secret = pyotp.random_base32()

    qr_code_base64_str = __generate_otp_qrcode(otp_secret, user_form.cleaned_data['email'])

    context = {'user_form': user_form, 'challenge_questions_form': challenge_questions_form,
               'user_2fa_form': user_2fa_form, 'otp_secret': otp_secret, 'qrcode_img': qr_code_base64_str}
    return render(request, 'auth/register-2fa.html', context)


def __generate_otp_qrcode(otp_secret, user_email):
    """Generates TOTP QR Code base64 str for the given secret."""
    totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=user_email, issuer_name='CSDS444 Project')
    qr_code_img = qrcode.make(totp_uri)
    buff = BytesIO()
    qr_code_img.save(buff, format='JPEG')
    return base64.b64encode(buff.getvalue()).decode('ascii')


def login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(data=request.POST)
        if login_form.is_valid():
            django_auth_login(request, login_form.get_user())
            totp = pyotp.totp.TOTP(request.user.customuserdata.otp_secret)
            user_inputted_code = login_form.cleaned_data['otp_code']
            if totp.verify(user_inputted_code):
                return redirect('/')
            else:
                login_form.add_error('otp_code', 'Failed to authenticate: wrong 2FA code.')
    else:
        login_form = UserLoginForm(request)

    return render(request, 'auth/login.html', {'form': login_form})


def password_reset(request, user):
    cq1 = user.customuserdata.challenge_question_1
    cq2 = user.customuserdata.challenge_question_2
    cq3 = user.customuserdata.challenge_question_3
    first = True
    if request.method == 'POST':
        user_password_form = PasswordResetForm(user=user, data=request.POST)
        custom_data_form = ChallengeQuestionsResetForm(data=request.POST)
        if user_password_form.is_valid() and custom_data_form.is_valid():
            # Check if challenge question responses were correct:
            if custom_data_form.matches_challenge_questions(user.customuserdata):
                # Save user's new password:
                if user_password_form.is_valid() and user_password_form.validate(request):
                    user_password_form.save()
                    messages.success(request, f'Your password has been reset.')
                    return redirect('login')
                else:
                    first = False
            else:
                first = False
                custom_data_form.add_error(None, 'Failed challenge questions')
                context = {'user_password_form': user_password_form, 'custom_data_form': custom_data_form, 'cq1': cq1, 'cq2': cq2, 'cq3': cq3, 'first': first}
                return render(request, 'auth/password-reset.html', context)
    else:
        user_password_form = PasswordResetForm(user=None)
        custom_data_form = ChallengeQuestionsResetForm()

    context = {'user_password_form': user_password_form, 'custom_data_form': custom_data_form, 'cq1': cq1, 'cq2': cq2, 'cq3': cq3, 'first': first}
    return render(request, 'auth/password-reset.html', context)

def password_reset_email(request):
    if request.method == 'POST':
        user_password_form = EmailPasswordResetForm(data=request.POST)
        if user_password_form.is_valid():
            # Fetch user from claimed email:
            user = User.objects.get(email__exact=user_password_form.cleaned_data['email'])
            return password_reset(request, user)
    else:
        user_password_form = EmailPasswordResetForm()

    context = {'user_password_form': user_password_form}
    return render(request, 'auth/password-reset-email.html', context)
