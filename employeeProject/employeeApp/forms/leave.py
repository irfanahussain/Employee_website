from django import forms
from employeeApp.models import LeaveType, LeaveRequest, Employee, CalendarEvent, LeaveBalance


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'default_yearly_allocation', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_yearly_allocation': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'from_date', 'to_date', 'is_half_day', 'handover_employee', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_leave_type'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_from_date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_to_date'}),
            'is_half_day': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'id_is_half_day'}),
            'handover_employee': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details of your leave request'}),
        }
        labels = {
            'is_half_day': 'Half Day Leave',
            'handover_employee': 'Work Handover Employee',
        }

    def __init__(self, *args, employee=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leave_type'].queryset = LeaveType.objects.filter(is_active=True)
        self.fields['leave_type'].empty_label = None
        handover_qs = Employee.objects.filter(employment_status=Employee.EmploymentStatus.ACTIVE).order_by('full_name')
        if employee is not None:
            handover_qs = handover_qs.exclude(pk=employee.pk)
        self.fields['handover_employee'].queryset = handover_qs
        self.fields['handover_employee'].required = False
        self.fields['handover_employee'].empty_label = 'Select…'
        self.fields['is_half_day'].required = False


class LeaveDecisionForm(forms.Form):
    DECISION_CHOICES = [('APPROVED', 'Approve'), ('REJECTED', 'Reject')]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))


class LeaveBalanceForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['employee', 'leave_type', 'year', 'allocated', 'used']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocated': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(
            employment_status=Employee.EmploymentStatus.ACTIVE
        ).order_by('full_name')
        self.fields['leave_type'].queryset = LeaveType.objects.all()

    def clean(self):
        cleaned = super().clean()
        employee = cleaned.get('employee')
        leave_type = cleaned.get('leave_type')
        year = cleaned.get('year')
        if employee and leave_type and year:
            qs = LeaveBalance.objects.filter(employee=employee, leave_type=leave_type, year=year)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "A leave balance for this employee, leave type, and year already exists — edit it instead."
                )
        return cleaned


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'event_type', 'start_date', 'end_date', 'time', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
