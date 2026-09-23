import json
from django.contrib.auth import get_user_model
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
from employeeApp.utils import require_own_employee

User = get_user_model()


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
    employee = require_own_employee(request)
    if employee is None:
        return redirect('accounts:redirect_dashboard')
    requests_qs = LeaveRequest.objects.filter(employee=employee).select_related('leave_type')
    balances = LeaveBalance.objects.filter(employee=employee, year=timezone.now().year).select_related('leave_type')
    paginator = Paginator(requests_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'employeeApp/my_leave_requests.html', {'page_obj': page_obj, 'balances': balances})


@login_required
def apply_leave(request):
    employee = require_own_employee(request)
    if employee is None:
        return redirect('accounts:redirect_dashboard')

    next_url = request.GET.get('next') or request.POST.get('next')
    prefill_date = request.GET.get('date', '')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, employee=employee)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.calculate_days()

            # Business rule validations
            errors = []
            if leave_request.from_date < timezone.now().date():
                errors.append("Cannot apply for dates in the past.")
            if leave_request.has_overlap():
                errors.append("You already have leave requested or approved that overlaps these dates.")

            balance = leave_request.get_balance()
            if balance is None:
                errors.append(f"No leave balance found for {leave_request.leave_type.name} this year.")

            if errors:
                for e in errors:
                    messages.error(request, e)
            else:
                # Any shortfall against the available balance is recorded as Loss of Pay (LOP)
                # rather than blocking the request outright.
                paid_days, lop_days = leave_request.calculate_lop()
                leave_request.lop_days = lop_days

                # Skip the Team Lead stage if the employee has no assigned Team Lead.
                if not employee.reporting_team_lead:
                    leave_request.status = LeaveRequest.Status.PENDING_HR

                leave_request.save()

                if lop_days:
                    messages.warning(
                        request,
                        f"Leave request submitted. {lop_days} day(s) exceed your available balance and will be "
                        f"processed as Loss of Pay (LOP) once approved."
                    )
                else:
                    messages.success(request, "Leave request submitted successfully.")

                if employee.reporting_team_lead:
                    Notification.objects.create(
                        user=employee.reporting_team_lead,
                        message=f"New leave request from {employee.full_name}.",
                        notification_type='LEAVE_REQUEST',
                        related_object_id=leave_request.id,
                    )
                else:
                    for hr_user in User.objects.filter(role=User.Role.HR):
                        Notification.objects.create(
                            user=hr_user,
                            message=f"New leave request from {employee.full_name} (no Team Lead assigned).",
                            notification_type='LEAVE_REQUEST',
                            related_object_id=leave_request.id,
                        )

                if next_url == 'calendar':
                    return redirect('employeeApp:calendar_view')
                return redirect('employeeApp:my_leave_requests')
    else:
        initial = {}
        if prefill_date:
            initial = {'from_date': prefill_date, 'to_date': prefill_date}
        form = LeaveRequestForm(employee=employee, initial=initial)

    balances = LeaveBalance.objects.filter(employee=employee, year=timezone.now().year).select_related('leave_type')
    balance_map = {str(b.leave_type_id): float(b.remaining) for b in balances}
    return render(request, 'employeeApp/apply_leave.html', {
        'form': form, 'balance_map_json': json.dumps(balance_map), 'next_url': next_url,
    })


@login_required
def cancel_leave(request, pk):
    employee = require_own_employee(request)
    if employee is None:
        return redirect('accounts:redirect_dashboard')
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    if not (leave_request.is_pending() or leave_request.status == LeaveRequest.Status.APPROVED):
        messages.error(request, "This request cannot be cancelled.")
        return redirect('employeeApp:my_leave_requests')

    if leave_request.status == LeaveRequest.Status.APPROVED:
        balance = leave_request.get_balance()
        if balance:
            balance.used -= leave_request.paid_days
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


# ---------- Approval: Team Lead decides first, then HR gives final approval. ----------
# Admin can override and decide at either stage.

@login_required
def decide_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    user = request.user

    is_team_lead_for_this = (
        user.is_team_lead() and leave_request.employee.team and leave_request.employee.team.team_lead == user
    )
    is_admin = user.is_admin()
    is_hr = user.is_hr()

    can_decide_as_team_lead = is_team_lead_for_this and leave_request.status == LeaveRequest.Status.PENDING
    can_decide_as_hr = is_hr and leave_request.status == LeaveRequest.Status.PENDING_HR
    can_decide_as_admin = is_admin and leave_request.is_pending()

    if not (can_decide_as_team_lead or can_decide_as_hr or can_decide_as_admin):
        if user.can_manage_employees() or is_team_lead_for_this:
            messages.error(request, "This request isn't awaiting your decision at its current stage.")
        else:
            messages.error(request, "You do not have permission to decide on this request.")
        return redirect('employeeApp:my_leave_requests')

    acting_stage = 'HR' if (can_decide_as_hr or (can_decide_as_admin and leave_request.status == LeaveRequest.Status.PENDING_HR)) else 'TEAM_LEAD'

    if request.method == 'POST':
        form = LeaveDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            remarks = form.cleaned_data['remarks']
            now = timezone.now()

            if acting_stage == 'TEAM_LEAD':
                leave_request.team_lead_remarks = remarks
                leave_request.decided_by = user
                leave_request.decided_at = now
                if decision == LeaveRequest.Status.REJECTED:
                    leave_request.status = LeaveRequest.Status.REJECTED
                    leave_request.save()
                    Notification.objects.create(
                        user=leave_request.employee.user,
                        message="Your leave request was rejected by your Team Lead.",
                        notification_type='LEAVE_DECISION', related_object_id=leave_request.id,
                    )
                    messages.success(request, "Leave request rejected.")
                else:
                    if is_admin:
                        # Admin override: approve outright without a separate HR step.
                        leave_request.status = LeaveRequest.Status.APPROVED
                        leave_request.hr_decided_by = user
                        leave_request.hr_decided_at = now
                        leave_request.save()
                        _apply_leave_balance(leave_request)
                        Notification.objects.create(
                            user=leave_request.employee.user,
                            message="Your leave request has been approved.",
                            notification_type='LEAVE_DECISION', related_object_id=leave_request.id,
                        )
                        messages.success(request, "Leave request approved.")
                    else:
                        leave_request.status = LeaveRequest.Status.PENDING_HR
                        leave_request.save()
                        Notification.objects.create(
                            user=leave_request.employee.user,
                            message="Your leave request was approved by your Team Lead and is now with HR for final approval.",
                            notification_type='LEAVE_DECISION', related_object_id=leave_request.id,
                        )
                        for hr_user in User.objects.filter(role=User.Role.HR):
                            Notification.objects.create(
                                user=hr_user,
                                message=f"Leave request from {leave_request.employee.full_name} awaits your final approval.",
                                notification_type='LEAVE_REQUEST', related_object_id=leave_request.id,
                            )
                        messages.success(request, "Leave request approved and forwarded to HR.")
            else:  # HR stage
                leave_request.hr_remarks = remarks
                leave_request.hr_decided_by = user
                leave_request.hr_decided_at = now
                leave_request.status = decision
                leave_request.save()
                if decision == LeaveRequest.Status.APPROVED:
                    _apply_leave_balance(leave_request)
                Notification.objects.create(
                    user=leave_request.employee.user,
                    message=f"Your leave request has been {decision.lower()} by HR.",
                    notification_type='LEAVE_DECISION', related_object_id=leave_request.id,
                )
                messages.success(request, f"Leave request {decision.lower()}.")

            if is_admin:
                return redirect('employeeApp:all_leave_requests')
            return redirect('employeeApp:team_leave_requests' if acting_stage == 'TEAM_LEAD' else 'employeeApp:all_leave_requests')
    else:
        form = LeaveDecisionForm()
    return render(request, 'employeeApp/decide_leave.html', {
        'form': form, 'leave_request': leave_request, 'acting_stage': acting_stage,
    })


def _apply_leave_balance(leave_request):
    balance = leave_request.get_balance()
    if balance:
        balance.used += leave_request.paid_days
        balance.save()


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
