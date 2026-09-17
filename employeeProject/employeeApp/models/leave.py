from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .employees import Employee


class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    default_yearly_allocation = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances')
    year = models.PositiveIntegerField(default=timezone.now().year)
    allocated = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"

    @property
    def remaining(self):
        return self.allocated - self.used


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests')
    from_date = models.DateField()
    to_date = models.DateField()
    number_of_days = models.DecimalField(max_digits=5, decimal_places=1, editable=False, default=0)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    team_lead_remarks = models.TextField(blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_decisions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.from_date} to {self.to_date})"

    def clean(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValidationError("To Date cannot be before From Date.")
        if self.from_date and self.from_date < timezone.now().date():
            raise ValidationError("Cannot apply for leave in the past.")

    def calculate_days(self):
        if self.from_date and self.to_date:
            self.number_of_days = (self.to_date - self.from_date).days + 1
        return self.number_of_days

    def has_overlap(self):
        return LeaveRequest.objects.filter(
            employee=self.employee, status=self.Status.APPROVED,
            from_date__lte=self.to_date, to_date__gte=self.from_date,
        ).exclude(pk=self.pk).exists()

    def get_balance(self):
        return LeaveBalance.objects.filter(
            employee=self.employee, leave_type=self.leave_type, year=self.from_date.year
        ).first()
