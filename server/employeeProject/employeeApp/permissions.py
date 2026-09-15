from rest_framework.permissions import SAFE_METHODS, BasePermission


def _employee_role(request):
    employee = getattr(request.user, "employee", None)
    return getattr(employee, "role", None)


class IsAdminOrHR(BasePermission):
    """Full access for Admin/HR. Used on Employee, Department, Team CRUD viewsets."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and _employee_role(
            request
        ) in ("admin", "hr")


class IsAdminOrHRorReadOnly(BasePermission):
    """Team Leads / Employees get read-only access (e.g. viewing departments)."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _employee_role(request) in ("admin", "hr")
