from django.urls import path
from . import views

app_name = 'employeeApp'

urlpatterns = [
    # Dashboards
    path('dashboard/admin-hr/', views.admin_hr_dashboard, name='admin_hr_dashboard'),
    path('dashboard/team-lead/', views.team_lead_dashboard, name='team_lead_dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),

    # Organization: Departments & Teams
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_form_view, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_form_view, name='department_edit'),
    path('teams/', views.team_list, name='team_list'),
    path('teams/add/', views.team_form_view, name='team_add'),
    path('teams/<int:pk>/edit/', views.team_form_view, name='team_edit'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_form_view, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_form_view, name='employee_edit'),
    path('employees/<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),

    # Attendance
    path('attendance/check-in/', views.check_in, name='check_in'),
    path('attendance/check-out/', views.check_out, name='check_out'),
    path('attendance/my/', views.my_attendance, name='my_attendance'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/<int:pk>/lock/', views.lock_attendance, name='lock_attendance'),

    # Leave types
    path('leave-types/', views.leave_type_list, name='leave_type_list'),
    path('leave-types/add/', views.leave_type_form_view, name='leave_type_add'),
    path('leave-types/<int:pk>/edit/', views.leave_type_form_view, name='leave_type_edit'),
    path('leave-types/<int:pk>/toggle/', views.leave_type_toggle, name='leave_type_toggle'),

    # Leave requests
    path('leave/my/', views.my_leave_requests, name='my_leave_requests'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),
    path('leave/team/', views.team_leave_requests, name='team_leave_requests'),
    path('leave/<int:pk>/decide/', views.decide_leave, name='decide_leave'),
    path('leave/all/', views.all_leave_requests, name='all_leave_requests'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/add-event/', views.add_calendar_event, name='add_calendar_event'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_read, name='mark_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # Reports
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/leave/', views.leave_report, name='leave_report'),
]
    

