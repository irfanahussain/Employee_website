from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        HOLIDAY='HOLIDAY','Office Leave/Holiday'
        OFFICE_EVENT='OFFICE_EVENT','Office Event'
        MEETING='MEETING','Scheduled Meeting'

    title=models.CharField(max_length=150)
    event_type=models.CharField(max_length=15,choices=EventType.choices,default=EventType.OFFICE_EVENT)
    start_date=models.DateField()
    end_date=models.DateField()
    time=models.TimeField(null=True,blank=True,help_text="Optional — mainly used for scheduled meetings.")
    description=models.TextField(blank=True)
    created_by=models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='calendar_events'
    )
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date})"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
