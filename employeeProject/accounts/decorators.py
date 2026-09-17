from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """Restrict a view to users whose .role is in `roles`."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# Convenience shortcuts matching the spec's permission matrix
admin_hr_required = role_required('ADMIN', 'HR')
admin_hr_teamlead_required = role_required('ADMIN', 'HR', 'TEAM_LEAD')
