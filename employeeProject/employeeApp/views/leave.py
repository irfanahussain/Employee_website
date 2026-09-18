from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.decorators import admin_hr_required, admin_hr_teamlead_required
from employeeApp.models import Employee
from employeeApp.models import Notification
from employeeApp.models import LeaveType, LeaveBalance, LeaveRequest
from employeeApp.forms import LeaveTypeForm, LeaveRequestForm, LeaveDecisionForm


# ---------- Leave Types (Admin/HR) ----------

@admin_hr_required
def leave_type_list(request):
    leave_types = LeaveType.objects.all()
    return render(request, 'employeeApp/leave_type_list.html', {'leave_types': leave_types})


@admin_hr_required
def leave_type_form_view(request, pk=None):
    leave_type = get_object_or_404(LeaveType, pk=pk) if pk else None
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, f"Leave type {'updated' if pk else 'created'} successfully.")
            return redirect('employeeApp:leave_type_list')
    else:
        form = LeaveTypeForm(instance=leave_type)
    return render(request, 'employeeApp/leave_type_form.html', {'form': form, 'leave_type': leave_type})


@admin_hr_required
def leave_type_toggle(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    leave_type.is_active = not leave_type.is_active
    leave_type.save()
    return redirect('employeeApp:leave_type_list')


# ---------- Employee: apply & view own ----------

@login_required
def my_leave_requests(request):
    employee = get_object_or_404(Employee, user=request.user)
    requests_qs = LeaveRequest.objects.filter(employee=employee).select_related('leave_type')
    balances = LeaveBalance.objects.filter(employee=employee, year=timezone.now().year).select_related('leave_type')
    paginator = Paginator(requests_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/my_leave_requests.html', {'page_obj': page_obj, 'balances': balances})


@login_required
def apply_leave(request):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.calculate_days()

            # Business rule validations
            errors = []
            if leave_request.from_date < timezone.now().date():
                errors.append("Cannot apply for dates in the past.")
            if leave_request.has_overlap():
                errors.append("You already have approved leave overlapping these dates.")

            balance = leave_request.get_balance()
            if balance is None:
                errors.append(f"No leave balance found for {leave_request.leave_type.name} this year.")
            elif balance.remaining < leave_request.number_of_days:
                errors.append(f"Insufficient balance. Remaining: {balance.remaining} day(s).")

            if errors:
                for e in errors:
                    messages.error(request, e)
            else:
                leave_request.save()
                messages.success(request, "Leave request submitted successfully.")
                if employee.reporting_team_lead:
                    Notification.objects.create(
                        user=employee.reporting_team_lead,
                        message=f"New leave request from {employee.full_name}.",
                        notification_type='LEAVE_REQUEST',
                        related_object_id=leave_request.id,
                    )
                return redirect('employeeApp:my_leave_requests')
    else:
        form = LeaveRequestForm()
    return render(request, 'employeeApp/apply_leave.html', {'form': form})


@login_required
def cancel_leave(request, pk):
    employee = get_object_or_404(Employee, user=request.user)
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    if leave_request.status not in (LeaveRequest.Status.PENDING, LeaveRequest.Status.APPROVED):
        messages.error(request, "This request cannot be cancelled.")
        return redirect('employeeApp:my_leave_requests')

    if leave_request.status == LeaveRequest.Status.APPROVED:
        balance = leave_request.get_balance()
        if balance:
            balance.used -= leave_request.number_of_days
            balance.save()

    leave_request.status = LeaveRequest.Status.CANCELLED
    leave_request.save()
    messages.success(request, "Leave request cancelled.")
    return redirect('employeeApp:my_leave_requests')


# ---------- Team Lead: team requests ----------

@login_required
def team_leave_requests(request):
    if not request.user.is_team_lead():
        return redirect('employeeApp:my_leave_requests')
    requests_qs = LeaveRequest.objects.filter(
        employee__team__team_lead=request.user
    ).select_related('employee', 'leave_type').order_by('-created_at')
    status = request.GET.get('status')
    if status:
        requests_qs = requests_qs.filter(status=status)
    paginator = Paginator(requests_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/team_leave_requests.html', {
        'page_obj': page_obj, 'statuses': LeaveRequest.Status.choices, 'status': status or ''
    })


# ---------- Approval (Team Lead for own team, Admin/HR for all + override) ----------

@login_required
def decide_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    user = request.user

    is_team_lead_for_this = user.is_team_lead() and leave_request.employee.team and leave_request.employee.team.team_lead == user
    if not (user.can_manage_employees() or is_team_lead_for_this):
        messages.error(request, "You do not have permission to decide on this request.")
        return redirect('employeeApp:my_leave_requests')

    if request.method == 'POST':
        form = LeaveDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            remarks = form.cleaned_data['remarks']

            leave_request.status = decision
            leave_request.team_lead_remarks = remarks
            leave_request.decided_by = user
            leave_request.decided_at = timezone.now()
            leave_request.save()

            if decision == LeaveRequest.Status.APPROVED:
                balance = leave_request.get_balance()
                if balance:
                    balance.used += leave_request.number_of_days
                    balance.save()

            Notification.objects.create(
                user=leave_request.employee.user,
                message=f"Your leave request has been {decision.lower()}.",
                notification_type='LEAVE_DECISION',
                related_object_id=leave_request.id,
            )
            messages.success(request, f"Leave request {decision.lower()}.")
            return redirect('employeeApp:team_leave_requests' if is_team_lead_for_this and not user.can_manage_employees()
                             else 'leave:all_leave_requests')
    else:
        form = LeaveDecisionForm()
    return render(request, 'employeeApp/decide_leave.html', {'form': form, 'leave_request': leave_request})


# ---------- Admin/HR: all requests + override ----------

@admin_hr_required
def all_leave_requests(request):
    requests_qs = LeaveRequest.objects.select_related('employee', 'leave_type').order_by('-created_at')
    status = request.GET.get('status')
    employee_id = request.GET.get('employee')
    if status:
        requests_qs = requests_qs.filter(status=status)
    if employee_id:
        requests_qs = requests_qs.filter(employee_id=employee_id)
    paginator = Paginator(requests_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/all_leave_requests.html', {
        'page_obj': page_obj, 'statuses': LeaveRequest.Status.choices, 'status': status or ''
    })
