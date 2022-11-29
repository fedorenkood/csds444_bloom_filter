from django.contrib import admin

# Register your models here.
from auth_ui.models import CustomUserData

admin.site.register(CustomUserData)