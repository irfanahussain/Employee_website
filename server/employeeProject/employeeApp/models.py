from django.db import models
from django.conf import settings

# Create your models here.

User=settings.AUTH_USER_MODEL


class Department(models.Model):
    name=models.CharField(max_length=120, unique=True)
    description=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    name=models.CharField(max_length=120)
    department=models.ForeignKey(
        Department,on_delete=models.CASCADE,related_name="teams"
    )
    team_lead=models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="led_teams",
    )
    description=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["department__name", "name"]
        unique_together=("name", "department")

    def __str__(self):
        return f"{self.department.name}/{self.name}"


class Employee(models.Model):
    ROLE_ADMIN="admin"
    ROLE_HR="hr"
    ROLE_TEAM_LEAD="team_lead"
    ROLE_EMPLOYEE="employee"
    ROLE_CHOICES=[
        (ROLE_ADMIN,"Admin"),
        (ROLE_HR,"HR"),
        (ROLE_TEAM_LEAD,"Team Lead"),
        (ROLE_EMPLOYEE,"Employee"),
    ]

    STATUS_ACTIVE="active"
    STATUS_INACTIVE="inactive"
    STATUS_CHOICES=[
        (STATUS_ACTIVE,"Active"),
        (STATUS_INACTIVE,"Inactive"),
    ]

    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="employee")
    employee_id=models.CharField(max_length=20,unique=True)
    full_name=models.CharField(max_length=150)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=20,blank=True)
    date_of_joining=models.DateField()
    department=models.ForeignKey(
        Department,on_delete=models.PROTECT,related_name="employees"
    )
    team = models.ForeignKey(
        Team,null=True,blank=True,on_delete=models.SET_NULL,related_name="members"
    )
    designation=models.CharField(max_length=120)
    role=models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)
    reporting_team_lead=models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )
    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    profile_image=models.ImageField(upload_to="profiles/", null=True, blank=True)
    address=models.CharField(max_length=255, blank=True)
    emergency_contact=models.CharField(max_length=50, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["-created_at"]

    def __str__(self):
        return f"{self.employee_id}—{self.full_name}"
