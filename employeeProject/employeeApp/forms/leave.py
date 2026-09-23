from django import forms
from employeeApp.models import LeaveType, LeaveRequest, Employee, CalendarEvent


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
