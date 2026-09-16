from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display=('username','email','role','is_active','is_staff')
    list_filter=('role','is_active')
    fieldsets=UserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role','phone','address','emergency_contact','profile_image')}),
    )
