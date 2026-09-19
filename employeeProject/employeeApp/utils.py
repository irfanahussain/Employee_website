from django.contrib import messages
from .models import Employee


def get_own_employee(request):
    """Return the Employee profile linked to request.user, or None if there isn't one yet."""
    try:
        return request.user.employee_profile
    except Employee.DoesNotExist:
        return None


def require_own_employee(request):
    """Look up the caller's own Employee profile.

    If it doesn't exist (e.g. an Admin/HR account that was never linked to an
    Employee record), queues a friendly error message and returns None so the
    calling view can redirect instead of raising a raw 404.
    """
    employee = get_own_employee(request)
    if employee is None:
        messages.error(
            request,
            "Your account isn't linked to an employee profile yet. "
            "Ask your Admin/HR to create one and link it to your user account."
        )
    return employee
