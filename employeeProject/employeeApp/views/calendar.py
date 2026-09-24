import calendar as pycalendar
import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import admin_hr_required
from employeeApp.forms import CalendarEventForm
from employeeApp.models import Attendance, CalendarEvent, LeaveBalance, LeaveRequest
from employeeApp.utils import get_own_employee

EVENT_TYPE_META = {
    'HOLIDAY': {'label': 'Office Leave / Holiday', 'css': 'holiday'},
    'OFFICE_EVENT': {'label': 'Office Event', 'css': 'office-event'},
    'MEETING': {'label': 'Scheduled Meetings', 'css': 'meeting'},
}

LEAVE_TYPE_CSS_FALLBACK = ['leave-1', 'leave-2', 'leave-3', 'leave-4']
LEAVE_TYPE_CSS_KEYWORDS = [
    ('casual', 'casual'), ('sick', 'sick'), ('comp', 'comp'),
]


def _css_for_leave_type(name, fallback_index):
    lowered = name.lower()
    for keyword, css in LEAVE_TYPE_CSS_KEYWORDS:
        if keyword in lowered:
            return css
    return LEAVE_TYPE_CSS_FALLBACK[fallback_index % len(LEAVE_TYPE_CSS_FALLBACK)]


@login_required
def calendar_view(request):
    today = timezone.now().date()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        date(year, month, 1)  # validate
    except (TypeError, ValueError):
        year, month = today.year, today.month

    first_day = date(year, month, 1)
    days_in_month = pycalendar.monthrange(year, month)[1]
    last_day = date(year, month, days_in_month)

    prev_month = (first_day.replace(day=1) - timedelta(days=1))
    next_month = (last_day + timedelta(days=1))

    employee = get_own_employee(request)

    # ---- Build per-day event buckets ----
    day_events = {d: [] for d in range(1, days_in_month + 1)}

    org_events = CalendarEvent.objects.filter(start_date__lte=last_day, end_date__gte=first_day)
    for ev in org_events:
        span_start = max(ev.start_date, first_day)
        span_end = min(ev.end_date, last_day)
        d = span_start
        while d <= span_end:
            meta = EVENT_TYPE_META.get(ev.event_type, {'label': ev.get_event_type_display(), 'css': 'office-event'})
            day_events[d.day].append({
                'label': ev.title, 'css': meta['css'], 'kind': meta['label'],
                'time': ev.time.strftime('%I:%M %p').lstrip('0') if ev.time else None,
            })
            d += timedelta(days=1)

    leave_type_css = {}
    if employee:
        leave_requests = LeaveRequest.objects.filter(
            employee=employee, from_date__lte=last_day, to_date__gte=first_day,
        ).exclude(status=LeaveRequest.Status.CANCELLED).select_related('leave_type')
        for lr in leave_requests:
            if lr.leave_type_id not in leave_type_css:
                leave_type_css[lr.leave_type_id] = _css_for_leave_type(lr.leave_type.name, len(leave_type_css))
            span_start = max(lr.from_date, first_day)
            span_end = min(lr.to_date, last_day)
            d = span_start
            while d <= span_end:
                status_label = lr.get_status_display()
                label = f"{lr.leave_type.name}{' (Half Day)' if lr.is_half_day else ''}"
                if lr.status == LeaveRequest.Status.REJECTED:
                    css = 'rejected'
                elif lr.is_pending():
                    css = 'pending-leave'
                else:
                    css = leave_type_css[lr.leave_type_id]
                day_events[d.day].append({
                    'label': label, 'css': css, 'kind': f"{status_label}",
                    'time': None,
                })
                if lr.lop_days and lr.status == LeaveRequest.Status.APPROVED:
                    day_events[d.day].append({'label': f"LOP: {lr.lop_days} day(s)", 'css': 'lop', 'kind': 'Loss of Pay', 'time': None})
                d += timedelta(days=1)

        attendance_qs = Attendance.objects.filter(employee=employee, date__gte=first_day, date__lte=last_day)
        for att in attendance_qs:
            if att.status == Attendance.Status.LATE:
                day_events[att.date.day].append({
                    'label': f"Late ({att.check_in.strftime('%I:%M %p').lstrip('0')})" if att.check_in else 'Late Check-in',
                    'css': 'late', 'kind': 'Late Check-in', 'time': None,
                })

    # ---- Build the month grid (Sun-first, matching the legend order) ----
    first_weekday = (first_day.weekday() + 1) % 7  # Python: Mon=0 -> convert to Sun=0
    weeks = []
    week = [None] * first_weekday
    for day_num in range(1, days_in_month + 1):
        week.append({'day': day_num, 'date': date(year, month, day_num), 'events': day_events[day_num]})
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        weeks.append(week)

    balances = []
    if employee:
        balances = LeaveBalance.objects.filter(employee=employee, year=today.year).select_related('leave_type')
    total_available = sum((b.remaining for b in balances), 0)
    total_taken = sum((b.used for b in balances), 0)

    leave_form = None
    if employee:
        from employeeApp.forms import LeaveRequestForm
        leave_form = LeaveRequestForm(employee=employee)
        balance_map = {str(b.leave_type_id): float(b.remaining) for b in balances}
    else:
        balance_map = {}

    context = {
        'year': year, 'month': month, 'month_name': first_day.strftime('%B'),
        'weeks': weeks, 'today': today,
        'prev_year': prev_month.year, 'prev_month': prev_month.month,
        'next_year': next_month.year, 'next_month': next_month.month,
        'leave_form': leave_form,
        'balance_map_json': json.dumps(balance_map),
        'balances': balances, 'total_available': total_available, 'total_taken': total_taken,
        'has_employee': employee is not None,
    }
    return render(request, 'employeeApp/calendar.html', context)


@admin_hr_required
def calendar_event_list(request):
    events = CalendarEvent.objects.all().order_by('-start_date')
    return render(request, 'employeeApp/calendar_event_list.html', {'events': events})


@admin_hr_required
def calendar_event_form_view(request, pk=None):
    event = get_object_or_404(CalendarEvent, pk=pk) if pk else None
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            saved_event = form.save(commit=False)
            if not pk:
                saved_event.created_by = request.user
            saved_event.save()
            messages.success(request, f"Calendar entry {'updated' if pk else 'added'} successfully.")
            return redirect('employeeApp:calendar_event_list')
    else:
        form = CalendarEventForm(instance=event)
    return render(request, 'employeeApp/calendar_event_form.html', {'form': form, 'event': event})


@admin_hr_required
def calendar_event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    event.delete()
    messages.success(request, "Calendar entry removed.")
    return redirect('employeeApp:calendar_event_list')
