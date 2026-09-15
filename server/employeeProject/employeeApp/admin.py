from django.contrib import admin
from .models import Department,Employee,Team

# Register your models here.
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display=("name", "is_active", "created_at")
    search_fields=("name",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display=("name", "department", "team_lead", "is_active")
    list_filter=("department", "is_active")
    search_fields=("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=(
        "employee_id",
        "full_name",
        "department",
        "team",
        "role",
        "status",
    )
    list_filter=("department","team","role","status")
    search_fields=("employee_id","full_name","email")
