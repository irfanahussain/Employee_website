from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        HR = 'HR', 'HR'
        TEAM_LEAD = 'TEAM_LEAD', 'Team Lead'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_hr(self):
        return self.role == self.Role.HR

    def is_team_lead(self):
        return self.role == self.Role.TEAM_LEAD

    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    def can_manage_employees(self):
        return self.role in (self.Role.ADMIN, self.Role.HR)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
