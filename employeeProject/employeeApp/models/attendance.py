from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .employees import Employee


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        HALF_DAY = 'HALF_DAY', 'Half Day'
        LATE = 'LATE', 'Late'
        LEAVE = 'LEAVE', 'Leave'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    def clean(self):
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError("Check-out time cannot be earlier than or equal to check-in time.")

    def calculate_working_hours(self):
        if self.check_in and self.check_out:
            today = timezone.now().date()
            start = timezone.datetime.combine(today, self.check_in)
            end = timezone.datetime.combine(today, self.check_out)
            delta = end - start
            hours = round(delta.total_seconds() / 3600, 2)
            self.working_hours = hours
            # business rule: < 4 hours counted as half day, > 4 and checked in late counted as late
            if hours < 4:
                self.status = self.Status.HALF_DAY
        return self.working_hours

    def is_lockable(self, lock_after_days):
        return (timezone.now().date() - self.date).days > lock_after_days
