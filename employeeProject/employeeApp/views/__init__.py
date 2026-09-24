from .organization import department_list, department_form_view, team_list, team_form_view
from .employees import employee_list, employee_detail, employee_form_view, employee_toggle_status
from .attendance import check_in, check_out, my_attendance, attendance_list, lock_attendance
from .leave import (
    leave_type_list, leave_type_form_view, leave_type_toggle,
    leave_balance_list, leave_balance_form_view, leave_balance_delete,
    my_leave_requests, apply_leave, cancel_leave,
    team_leave_requests, decide_leave, all_leave_requests,
)
from .notifications import notification_list, mark_read, mark_all_read
from .dashboard import admin_hr_dashboard, team_lead_dashboard, employee_dashboard
from .reports import attendance_report, leave_report
from .calendar import calendar_view, calendar_event_list, calendar_event_form_view, calendar_event_delete
