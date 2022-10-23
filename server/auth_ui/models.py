from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserData(models.Model):
    """Custom User Data for storing challenge questions and any other extra user data.
    See: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    challenge_question_1 = models.CharField(max_length=200)
    challenge_question_2 = models.CharField(max_length=200)
    challenge_question_3 = models.CharField(max_length=200)

@receiver(post_save, sender=User)
def create_user_custom_data(sender, instance, created, **kwargs):
    if created:
        CustomUserData.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_custom_data(sender, instance, **kwargs):
    instance.customuserdata.save()
