from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from accounts.decorators import admin_hr_required
from employeeApp.models import Department, Team
from employeeApp.forms.organization import DepartmentForm, TeamForm


@admin_hr_required
def department_list(request):
    departments = Department.objects.all()
    q = request.GET.get('q')
    if q:
        departments = departments.filter(name__icontains=q)
    paginator = Paginator(departments, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/department_list.html', {'page_obj': page_obj, 'q': q or ''})


@admin_hr_required
def department_form_view(request, pk=None):
    department = get_object_or_404(Department, pk=pk) if pk else None
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department {'updated' if pk else 'created'} successfully.")
            return redirect('organization:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'employeeApp/department_form.html', {'form': form, 'department': department})


@admin_hr_required
def team_list(request):
    teams = Team.objects.select_related('department', 'team_lead').all()
    dept_id = request.GET.get('department')
    if dept_id:
        teams = teams.filter(department_id=dept_id)
    q = request.GET.get('q')
    if q:
        teams = teams.filter(name__icontains=q)
    paginator = Paginator(teams, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/team_list.html', {
        'page_obj': page_obj, 'departments': Department.objects.all(), 'q': q or '', 'dept_id': dept_id or ''
    })


@admin_hr_required
def team_form_view(request, pk=None):
    team = get_object_or_404(Team, pk=pk) if pk else None
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, f"Team {'updated' if pk else 'created'} successfully.")
            return redirect('organization:team_list')
    else:
        form = TeamForm(instance=team)
    return render(request, 'employeeApp/team_form.html', {'form': form, 'team': team})
