from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from employeeApp.models import Attendance, LeaveRequest, Employee, Department


def _scope_employees(user):
    """Admin/HR see all employees; Team Lead sees their team; Employee sees only self."""
    if user.can_manage_employees():
        return Employee.objects.all()
    if user.is_team_lead():
        return Employee.objects.filter(team__team_lead=user)
    return Employee.objects.filter(user=user)


@login_required
def attendance_report(request):
    employees = _scope_employees(request.user)
    records = Attendance.objects.filter(employee__in=employees).select_related(
        'employee', 'employee__team', 'employee__team__department')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    status = request.GET.get('status')

    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)
    if employee_id:
        records = records.filter(employee_id=employee_id)
    if department_id:
        records = records.filter(employee__team__department_id=department_id)
    if status:
        records = records.filter(status=status)

    totals = {
        'total_working_days': records.count(),
        'present_days': records.filter(status__in=['PRESENT', 'LATE']).count(),
        'absent_days': records.filter(status='ABSENT').count(),
        'leave_days': records.filter(status='LEAVE').count(),
        'late_days': records.filter(status='LATE').count(),
    }

    return render(request, 'employeeApp/attendance_report.html', {
        'records': records.order_by('-date')[:200],
        'totals': totals,
        'departments': Department.objects.filter(is_active=True),
        'statuses': Attendance.Status.choices,
        'filters': {
            'date_from': date_from or '', 'date_to': date_to or '',
            'employee': employee_id or '', 'department': department_id or '', 'status': status or '',
        },
    })


@login_required
def leave_report(request):
    employees = _scope_employees(request.user)
    requests_qs = LeaveRequest.objects.filter(employee__in=employees).select_related(
        'employee', 'leave_type', 'employee__team', 'employee__team__department')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    leave_type_id = request.GET.get('leave_type')
    status = request.GET.get('status')

    if date_from:
        requests_qs = requests_qs.filter(from_date__gte=date_from)
    if date_to:
        requests_qs = requests_qs.filter(to_date__lte=date_to)
    if employee_id:
        requests_qs = requests_qs.filter(employee_id=employee_id)
    if department_id:
        requests_qs = requests_qs.filter(employee__team__department_id=department_id)
    if leave_type_id:
        requests_qs = requests_qs.filter(leave_type_id=leave_type_id)
    if status:
        requests_qs = requests_qs.filter(status=status)

    from employeeApp.models import LeaveType
    total_leave_days = sum(r.number_of_days for r in requests_qs.filter(status='APPROVED'))

    return render(request, 'employeeApp/leave_report.html', {
        'requests': requests_qs.order_by('-from_date')[:200],
        'total_leave_days': total_leave_days,
        'departments': Department.objects.filter(is_active=True),
        'leave_types': LeaveType.objects.all(),
        'statuses': LeaveRequest.Status.choices,
        'filters': {
            'date_from': date_from or '', 'date_to': date_to or '', 'employee': employee_id or '',
            'department': department_id or '', 'leave_type': leave_type_id or '', 'status': status or '',
        },
    })
