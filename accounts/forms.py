from django import forms
from django.contrib.auth.models import User

# Simple User Register Form
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'clean-input', 'placeholder': 'Password'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'clean-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'clean-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'clean-input', 'placeholder': 'Email'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

# Membership Signup Form
class MembershipSignupForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'clean-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'clean-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'clean-input', 'placeholder': 'Email'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'clean-input', 'placeholder': 'Phone'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'clean-input', 'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email