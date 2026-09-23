from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        LEAVE_REQUEST='LEAVE_REQUEST', 'Leave Request'
        LEAVE_DECISION='LEAVE_DECISION','Leave Decision'
        ATTENDANCE='ATTENDANCE','Attendance'
        GENERAL='GENERAL','General'

    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message=models.CharField(max_length=255)
    notification_type=models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL)
    related_object_id=models.PositiveIntegerField(null=True, blank=True)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return f"{self.user} - {self.message[:40]}"
