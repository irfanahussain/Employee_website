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
        PENDING = 'PENDING', 'Pending Team Lead'
        PENDING_HR = 'PENDING_HR', 'Pending HR'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests')
    from_date = models.DateField()
    to_date = models.DateField()
    is_half_day = models.BooleanField(default=False)
    number_of_days = models.DecimalField(max_digits=5, decimal_places=1, editable=False, default=0)
    lop_days = models.DecimalField(
        max_digits=5, decimal_places=1, editable=False, default=0,
        help_text="Portion of number_of_days that exceeds the available balance and is treated as Loss of Pay."
    )
    handover_employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='handovers'
    )
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    # Team Lead stage
    team_lead_remarks = models.TextField(blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_decisions'
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    # HR stage (final approval)
    hr_remarks = models.TextField(blank=True)
    hr_decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_hr_decisions'
    )
    hr_decided_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.from_date} to {self.to_date})"

    def clean(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValidationError("To Date cannot be before From Date.")
        if self.from_date and self.from_date < timezone.now().date():
            raise ValidationError("Cannot apply for leave in the past.")
        if self.is_half_day and self.from_date and self.to_date and self.from_date != self.to_date:
            raise ValidationError("Half day leave can only be applied for a single date.")
        if self.handover_employee_id and self.employee_id and self.handover_employee_id == self.employee_id:
            raise ValidationError("You cannot set yourself as the work handover employee.")

    def calculate_days(self):
        if self.is_half_day:
            self.number_of_days = 0.5
        elif self.from_date and self.to_date:
            self.number_of_days = (self.to_date - self.from_date).days + 1
        return self.number_of_days

    def has_overlap(self):
        return LeaveRequest.objects.filter(
            employee=self.employee, status__in=[self.Status.APPROVED, self.Status.PENDING, self.Status.PENDING_HR],
            from_date__lte=self.to_date, to_date__gte=self.from_date,
        ).exclude(pk=self.pk).exists()

    def get_balance(self):
        return LeaveBalance.objects.filter(
            employee=self.employee, leave_type=self.leave_type, year=self.from_date.year
        ).first()

    def calculate_lop(self):
        """Split number_of_days into paid vs Loss-of-Pay based on remaining balance at apply time.

        Returns (paid_days, lop_days) without saving.
        """
        balance = self.get_balance()
        remaining = balance.remaining if balance else 0
        if remaining >= self.number_of_days:
            return self.number_of_days, 0
        paid = max(remaining, 0)
        lop = self.number_of_days - paid
        return paid, lop

    @property
    def paid_days(self):
        return self.number_of_days - self.lop_days

    def is_pending(self):
        return self.status in (self.Status.PENDING, self.Status.PENDING_HR)
