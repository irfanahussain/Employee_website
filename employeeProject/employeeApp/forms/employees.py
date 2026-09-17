from django import forms
from django.contrib.auth.hashers import make_password
from accounts.models import User
from employeeApp.models import Employee


class EmployeeForm(forms.ModelForm):
    """Used for both create and edit. On create, also provisions a login User account."""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    initial_password = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Only required when creating a new employee."
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'full_name', 'email', 'phone', 'date_of_joining',
            'designation', 'team', 'reporting_team_lead', 'employment_status',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'reporting_team_lead': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        if self.is_edit:
            self.fields.pop('username')
            self.fields.pop('role')
            self.fields.pop('initial_password')
        else:
            self.fields['initial_password'].required = True

    def save(self, commit=True):
        employee = super().save(commit=False)
        if not self.is_edit:
            user = User.objects.create(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['full_name'].split(' ')[0],
                role=self.cleaned_data['role'],
                password=make_password(self.cleaned_data['initial_password']),
            )
            employee.user = user
        if commit:
            employee.save()
        return employee


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']
