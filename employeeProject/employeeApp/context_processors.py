from employeeApp.models import Notification


def unread_notifications(request):
    """Makes unread notification count/list available in every template."""
    if request.user.is_authenticated:
        qs = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notification_count': qs.count(),
            'recent_notifications': qs[:5],
        }
    return {'unread_notification_count': 0, 'recent_notifications': []}
