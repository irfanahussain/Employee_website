from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import admin_hr_required, role_required
from employeeApp.models import Employee
from employeeApp.models import Attendance
from employeeApp.models import LeaveRequest, LeaveBalance
from employeeApp.models import Department
from employeeApp.utils import require_own_employee


@admin_hr_required
def admin_hr_dashboard(request):
    today = timezone.localdate()
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='ACTIVE').count()
    todays_present = Attendance.objects.filter(date=today, status__in=['PRESENT', 'LATE']).count()
    todays_absent = active_employees - todays_present
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    approved_leaves = LeaveRequest.objects.filter(status='APPROVED').count()
    dept_counts = [(d.name, d.employee_count()) for d in Department.objects.filter(is_active=True)]

    monthly_summary = Attendance.objects.filter(date__year=today.year, date__month=today.month) \
        .values('status').order_by('status')
    status_counts = {}
    for row in monthly_summary:
        status_counts[row['status']] = status_counts.get(row['status'], 0) + 1

    return render(request, 'employeeApp/admin_hr_dashboard.html', {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'todays_present': todays_present,
        'todays_absent': todays_absent,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'dept_counts': dept_counts,
        'status_counts': status_counts,
    })


@role_required('TEAM_LEAD')
def team_lead_dashboard(request):
    today = timezone.localdate()
    team_members = Employee.objects.filter(team__team_lead=request.user)
    todays_attendance = Attendance.objects.filter(employee__in=team_members, date=today)
    pending_team_leaves = LeaveRequest.objects.filter(employee__in=team_members, status='PENDING')
    approved_team_leaves = LeaveRequest.objects.filter(employee__in=team_members, status='APPROVED')

    return render(request, 'employeeApp/team_lead_dashboard.html', {
        'team_members_count': team_members.count(),
        'todays_attendance': todays_attendance,
        'pending_team_leaves': pending_team_leaves,
        'approved_team_leaves_count': approved_team_leaves.count(),
    })


@login_required
def employee_dashboard(request):
    employee = require_own_employee(request)
    if employee is None:
        return redirect('accounts:redirect_dashboard')
    today = timezone.localdate()
    today_record = Attendance.objects.filter(employee=employee, date=today).first()
    leave_balances = LeaveBalance.objects.filter(employee=employee, year=today.year).select_related('leave_type')
    pending_requests = LeaveRequest.objects.filter(employee=employee, status='PENDING')
    recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:5]
    recent_leave_history = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:5]

    return render(request, 'employeeApp/employee_dashboard.html', {
        'today_record': today_record,
        'leave_balances': leave_balances,
        'pending_requests': pending_requests,
        'recent_attendance': recent_attendance,
        'recent_leave_history': recent_leave_history,
    })
