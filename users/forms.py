from django import forms
from phonenumber_field.formfields import PhoneNumberField as PhoneNumberFormField
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from users.models import Profile


User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists")
        return email


            

class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a role",
        widget=forms.Select(attrs={"class": "form-select"})
    )



class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "permissions"]
        widgets = {
            "permissions": forms.CheckboxSelectMultiple,
        }


class EditProfileForm(forms.ModelForm):
    phone_number = PhoneNumberFormField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number'
        }),
        required=False
    )
    
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_image']

class EditUserForm(forms.ModelForm):
    email = forms.EmailField(disabled=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']




class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your old password'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new password again'
        })
    )