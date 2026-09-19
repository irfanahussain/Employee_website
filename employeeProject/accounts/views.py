from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import LoginForm, ProfileForm, StyledPasswordResetForm, StyledSetPasswordForm
from accounts.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect_dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            intended_role = form.cleaned_data.get('intended_role')
            if intended_role and user.role != intended_role:
                form.add_error(
                    None,
                    f"This account is registered as {user.get_role_display()}, "
                    f"not {dict(User.Role.choices).get(intended_role, intended_role)}. "
                    f"Please select the correct tab and try again."
                )
            else:
                login(request, user)
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(settings.REMEMBER_ME_SESSION_AGE)
                else:
                    request.session.set_expiry(0)  # expires when the browser is closed
                return redirect('accounts:redirect_dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'roles': User.Role})


def request_access_view(request):
    """'Don't have an account?' — accounts are provisioned by Admin/HR, not self-serve."""
    return render(request, 'accounts/request_access.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def redirect_dashboard(request):
    role_map = {
        User.Role.ADMIN: 'employeeApp:admin_hr_dashboard',
        User.Role.HR: 'employeeApp:admin_hr_dashboard',
        User.Role.TEAM_LEAD: 'employeeApp:team_lead_dashboard',
        User.Role.EMPLOYEE: 'employeeApp:employee_dashboard',
    }
    return redirect(role_map.get(request.user.role, 'employeeApp:employee_dashboard'))


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')


@login_required
def password_change_done(request):
    messages.success(request, 'Your password was changed successfully.')
    return redirect('accounts:profile')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})