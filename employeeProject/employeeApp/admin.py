from django.contrib import admin
from .models import Department, Team, Employee, Attendance, LeaveType, LeaveBalance, LeaveRequest, Notification



# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'employee_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'team_lead', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'email', 'team', 'employment_status', 'date_of_joining')
    list_filter = ('employment_status', 'team__department', 'team')
    search_fields = ('employee_id', 'full_name', 'email')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'working_hours', 'status', 'is_locked')
    list_filter = ('status', 'date', 'is_locked')
    search_fields = ('employee__full_name', 'employee__employee_id')


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_yearly_allocation', 'is_active')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'year', 'allocated', 'used', 'remaining')
    list_filter = ('leave_type', 'year')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'from_date', 'to_date', 'number_of_days', 'status')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__full_name',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
