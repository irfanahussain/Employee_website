from django.shortcuts import render
import django_filters
from django.db.models import Count
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Department, Employee, Team
from .permissions import IsAdminOrHR, IsAdminOrHRorReadOnly
from .serializers import DepartmentSerializer, EmployeeSerializer, TeamSerializer
# Create your views here.


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter(field_name="department_id")
    team = django_filters.NumberFilter(field_name="team_id")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Employee
        fields = ["department", "team", "status", "role"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """Admin/HR: full CRUD. Section 4 of the brief."""

    queryset = Employee.objects.select_related("department", "team").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    pagination_class = StandardPagination
    filterset_class = EmployeeFilter
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ["full_name", "employee_id", "email", "designation"]

    def perform_update(self, serializer):
        # Activate/deactivate is just a status update through the same endpoint —
        # PATCH { "status": "inactive" } — no separate action needed.
        serializer.save()


class DepartmentViewSet(viewsets.ModelViewSet):
    """Section 5: Department & Team Management."""

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHRorReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related("department", "team_lead").all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHRorReadOnly]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_fields = ["department", "is_active"]
    search_fields = ["name"]


class AdminDashboardView(APIView):
    """Section 10: Admin/HR Dashboard stats."""

    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def get(self, request):
        employees = Employee.objects.all()
        department_counts = list(
            employees.values("department__name").annotate(count=Count("id")).order_by(
                "department__name"
            )
        )
        return Response(
            {
                "total_employees": employees.count(),
                "active_employees": employees.filter(status=Employee.STATUS_ACTIVE).count(),
                "department_wise_count": department_counts,
                # today's present/absent, pending/approved leaves plug in once
                # the Attendance and LeaveRequest models exist.
            }
        )
