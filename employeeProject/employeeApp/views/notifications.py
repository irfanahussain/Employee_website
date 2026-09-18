from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from employeeApp.models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/notification_list.html', {'page_obj': page_obj})


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('employeeApp:notification_list')


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('employeeApp:notification_list')
