from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'password1', 'password2', 'email']

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

            

class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a role",
        widget=forms.Select(attrs={"class": "form-select"})
    )

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"})
        }
