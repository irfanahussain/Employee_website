from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import LoginForm, ProfileForm
from accounts.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect_dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:redirect_dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


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