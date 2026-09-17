from django.db import models
from django.conf import settings
from .organization import Team


class Employee(models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_joining = models.DateField()
    designation = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    reporting_team_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='direct_reports', limit_choices_to={'role': 'TEAM_LEAD'}
    )
    employment_status = models.CharField(max_length=10, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    @property
    def department(self):
        return self.team.department if self.team else None

    def is_active_employee(self):
        return self.employment_status == self.EmploymentStatus.ACTIVE
