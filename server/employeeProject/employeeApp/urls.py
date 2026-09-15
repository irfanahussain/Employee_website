from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminDashboardView, DepartmentViewSet, EmployeeViewSet, TeamViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="department")
router.register("teams", TeamViewSet, basename="team")

urlpatterns = [
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("", include(router.urls)),
]
