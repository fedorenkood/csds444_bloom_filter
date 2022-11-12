from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from auth_ui.models import CustomUserData


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=101)
    last_name = forms.CharField(max_length=101)
    email = forms.EmailField()

    # TODO: Add custom error: https://stackoverflow.com/questions/18646450/customize-error-messages-on-django-registration

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class User2faValidationForm(forms.Form):
    validation_code = forms.CharField(max_length=50)


class ChallengeQuestionsForm(forms.ModelForm):
    def matches_challenge_questions(self, expected: CustomUserData) -> bool:
        """If challenge question answers of this form match those of the given other model."""
        return self.matches_challenge_question('challenge_question_1', expected.challenge_question_1) and \
               self.matches_challenge_question('challenge_question_2', expected.challenge_question_2) and \
               self.matches_challenge_question('challenge_question_3', expected.challenge_question_3)

    def matches_challenge_question(self: object, field: str, expected: str) -> bool:
        """If challenge question answer for given field matches the expected answer value."""
        # TODO: Sanitize
        return expected.lower() == self.cleaned_data[field].lower()

    class Meta:
        model = CustomUserData
        fields = ('challenge_question_1', 'challenge_question_2', 'challenge_question_3')


class PasswordResetForm(SetPasswordForm):
    """Note: usage is kind of dirty; this form doubles as both a raw anonymous input for email & new password,
    but also is used for the base class functionality of saving the new password given a registered user."""
    email = forms.EmailField()

    class Meta:
        fields = ['new_password1', 'new_password2', 'email']
