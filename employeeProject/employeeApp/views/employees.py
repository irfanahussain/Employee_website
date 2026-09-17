from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import admin_hr_required
from employeeApp.models import Department, Team
from employeeApp.models import Employee
from employeeApp.forms import EmployeeForm


@login_required
def employee_list(request):
    """Admin/HR see everyone; Team Lead sees their team; Employee sees only self (view-only)."""
    user = request.user
    if user.can_manage_employees():
        employees = Employee.objects.select_related('team', 'team__department', 'user')
    elif user.is_team_lead():
        employees = Employee.objects.filter(team__team_lead=user).select_related('team', 'team__department', 'user')
    else:
        employees = Employee.objects.filter(user=user).select_related('team', 'team__department', 'user')

    q = request.GET.get('q')
    department_id = request.GET.get('department')
    team_id = request.GET.get('team')
    status = request.GET.get('status')

    if q:
        employees = employees.filter(
            Q(full_name__icontains=q) | Q(employee_id__icontains=q) | Q(email__icontains=q)
        )
    if department_id:
        employees = employees.filter(team__department_id=department_id)
    if team_id:
        employees = employees.filter(team_id=team_id)
    if status:
        employees = employees.filter(employment_status=status)

    paginator = Paginator(employees, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'employeeApp/employee_list.html', {
        'page_obj': page_obj,
        'departments': Department.objects.filter(is_active=True),
        'teams': Team.objects.filter(is_active=True),
        'statuses': Employee.EmploymentStatus.choices,
        'filters': {'q': q or '', 'department': department_id or '', 'team': team_id or '', 'status': status or ''},
        'can_manage': user.can_manage_employees(),
    })


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = request.user
    if not (user.can_manage_employees() or user == employee.user or
            (user.is_team_lead() and employee.team and employee.team.team_lead == user)):
        messages.error(request, "You do not have permission to view this employee.")
        return redirect('employees:employee_list')
    return render(request, 'employeeApp/employee_detail.html', {'employee': employee})


@admin_hr_required
def employee_form_view(request, pk=None):
    employee = get_object_or_404(Employee, pk=pk) if pk else None
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, is_edit=bool(pk))
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee {'updated' if pk else 'added'} successfully.")
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm(instance=employee, is_edit=bool(pk))
    return render(request, 'employeeApp/employee_form.html', {'form': form, 'employee': employee})


@admin_hr_required
def employee_toggle_status(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if employee.employment_status == Employee.EmploymentStatus.ACTIVE:
        employee.employment_status = Employee.EmploymentStatus.INACTIVE
        employee.user.is_active = False
    else:
        employee.employment_status = Employee.EmploymentStatus.ACTIVE
        employee.user.is_active = True
    employee.user.save()
    employee.save()
    messages.success(request, f"{employee.full_name} is now {employee.employment_status.lower()}.")
    return redirect('employees:employee_list')
