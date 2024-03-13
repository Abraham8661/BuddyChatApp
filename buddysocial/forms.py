from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=200,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Enter your username"}),
    )
    email = forms.EmailField(
        max_length=200,
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": "Enter your email address"}),
    )
    password1 = forms.CharField(
        label = "Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder':'Enter your password'}),
    )
    password2 = forms.CharField(
        label = "Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder':'Confirm your password'}),
    )
    class Meta:
        model = User 
        fields = ("username", "email", "password1", "password2")


# class SignUpForm(UserCreationForm):
#    first_name = forms.CharField(max_length=20, required=True)
#    last_name = forms.CharField(max_length=20, required=True)
#    email = forms.EmailField(required=True)
#    phone_number = forms.CharField(max_length=11)
#
#    class Meta:
#        model = User
#        fields = (
#            "username",
#            "first_name",
#            "last_name",
#            "email",
#            "phone_number",
#            "password1",
#            "password2",
#        )
#
#
# class LoginForm(forms.Form):
#    username = forms.CharField(
#        label="Your Username",
#        validators=[MinLengthValidator(5, "This field cannot be empty")],
#    )
#    password = forms.CharField(
#        label="Your Password", widget=forms.PasswordInput, max_length=20
#    )
#
