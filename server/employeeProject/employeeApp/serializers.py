from rest_framework import serializers

from .models import Department, Employee, Team


class DepartmentSerializer(serializers.ModelSerializer):
    team_count = serializers.IntegerField(source="teams.count", read_only=True)
    employee_count = serializers.IntegerField(source="employees.count", read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "team_count",
            "employee_count",
            "created_at",
        ]


class TeamSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    team_lead_name = serializers.CharField(
        source="team_lead.get_full_name", read_only=True, default=""
    )
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "department",
            "department_name",
            "team_lead",
            "team_lead_name",
            "description",
            "is_active",
            "member_count",
            "created_at",
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default="")

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "full_name",
            "email",
            "phone",
            "date_of_joining",
            "department",
            "department_name",
            "team",
            "team_name",
            "designation",
            "role",
            "reporting_team_lead",
            "status",
            "profile_image",
            "address",
            "emergency_contact",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Restricted serializer for self-service profile edits (Section 13 of the brief)."""

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "full_name",
            "email",
            "phone",
            "profile_image",
            "address",
            "emergency_contact",
            "department_name",
            "designation",
            "date_of_joining",
            "role",
        ]
        read_only_fields = [
            "employee_id",
            "full_name",
            "email",
            "department_name",
            "designation",
            "date_of_joining",
            "role",
        ]
