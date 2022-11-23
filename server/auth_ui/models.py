from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


CHALLENGE_QUESTIONS = [
    ('what street did you grow up on?', 'What street did you grow up on?'),
    ('what was your first pet\'s name?', 'What was your first pet\'s name?'),
    ('what is your mom\'s maiden name?', 'What is your mom\'s maiden name?'),
    ('what high school did you attend?', 'What high school did you attend?'),
    ('what was the name of the boy or girl you first kissed?', 'What was the name of the boy or girl you first kissed?'),
    ('what was the first concert you attended?', 'What was the first concert you attended?'),
    ('what is your oldest sibling\'s middle name?', 'What is your oldest sibling\'s middle name?'),
    ('what was the name of your first stuffed toy?', 'What was the name of your first stuffed toy?'),
    ('where did you meet your spouse?', 'Where did you meet your spouse?'),
    ('what was the make of your first car?', 'What was the make of your first car?')
]

class CustomUserData(models.Model):
    """Custom User Data for storing challenge questions and any other extra user data.
    See: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    challenge_question_1 = models.CharField(max_length=200, choices=CHALLENGE_QUESTIONS)
    challenge_answer_1 = models.CharField(max_length=200, default=' ')
    challenge_question_2 = models.CharField(max_length=200, choices=CHALLENGE_QUESTIONS)
    challenge_answer_2 = models.CharField(max_length=200, default=' ')
    challenge_question_3 = models.CharField(max_length=200, choices=CHALLENGE_QUESTIONS)
    challenge_answer_3 = models.CharField(max_length=200, default=' ')

    otp_secret = models.CharField(max_length=100, default='')


@receiver(post_save, sender=User)
def create_user_custom_data(sender, instance, created, **kwargs):
    if created:
        CustomUserData.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_custom_data(sender, instance, **kwargs):
    instance.customuserdata.save()