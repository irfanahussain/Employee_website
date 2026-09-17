from datetime import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from accounts.decorators import admin_hr_required
from employeeApp.models import Employee
from employeeApp.models import Department
from employeeApp.models import Attendance

STANDARD_START_TIME = time(9, 30)  # after this, marked Late


@login_required
def check_in(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    existing = Attendance.objects.filter(employee=employee, date=today).first()
    if existing and existing.check_in:
        messages.error(request, "You have already checked in today.")
        return redirect('attendance:my_attendance')

    status = Attendance.Status.LATE if now_time > STANDARD_START_TIME else Attendance.Status.PRESENT
    if existing:
        existing.check_in = now_time
        existing.status = status
        existing.save()
    else:
        Attendance.objects.create(employee=employee, date=today, check_in=now_time, status=status)
    messages.success(request, f"Checked in at {now_time.strftime('%I:%M %p')}.")
    return redirect('attendance:my_attendance')


@login_required
def check_out(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    record = Attendance.objects.filter(employee=employee, date=today).first()
    if not record or not record.check_in:
        messages.error(request, "You must check in before checking out.")
        return redirect('attendance:my_attendance')
    if record.check_out:
        messages.error(request, "You have already checked out today.")
        return redirect('attendance:my_attendance')
    if now_time <= record.check_in:
        messages.error(request, "Check-out time cannot be earlier than check-in time.")
        return redirect('attendance:my_attendance')

    record.check_out = now_time
    record.calculate_working_hours()
    record.save()
    messages.success(request, f"Checked out at {now_time.strftime('%I:%M %p')}. Working hours: {record.working_hours}")
    return redirect('attendance:my_attendance')


@login_required
def my_attendance(request):
    employee = get_object_or_404(Employee, user=request.user)
    today = timezone.localdate()
    today_record = Attendance.objects.filter(employee=employee, date=today).first()
    history = Attendance.objects.filter(employee=employee).order_by('-date')
    paginator = Paginator(history, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/my_attendance.html', {
        'today_record': today_record, 'page_obj': page_obj,
    })


@login_required
def attendance_list(request):
    """Admin/HR: all records. Team Lead: team records (view only). Employee: redirected to my_attendance."""
    user = request.user
    if user.can_manage_employees():
        records = Attendance.objects.select_related('employee', 'employee__team', 'employee__team__department')
    elif user.is_team_lead():
        records = Attendance.objects.filter(employee__team__team_lead=user).select_related(
            'employee', 'employee__team', 'employee__team__department')
    else:
        return redirect('attendance:my_attendance')

    date_filter = request.GET.get('date')
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    month = request.GET.get('month')  # YYYY-MM for monthly view

    if date_filter:
        records = records.filter(date=date_filter)
    if employee_id:
        records = records.filter(employee_id=employee_id)
    if department_id:
        records = records.filter(employee__team__department_id=department_id)
    if status:
        records = records.filter(status=status)
    if month:
        try:
            year, mon = month.split('-')
            records = records.filter(date__year=year, date__month=mon)
        except ValueError:
            pass

    records = records.order_by('-date')
    paginator = Paginator(records, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'employeeApp/attendance_list.html', {
        'page_obj': page_obj,
        'departments': Department.objects.filter(is_active=True),
        'statuses': Attendance.Status.choices,
        'filters': {
            'date': date_filter or '', 'employee': employee_id or '',
            'department': department_id or '', 'status': status or '', 'month': month or '',
        },
    })


@admin_hr_required
def lock_attendance(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    record.is_locked = True
    record.save()
    messages.success(request, "Attendance record locked.")
    return redirect('attendance:attendance_list')
