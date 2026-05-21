from django import forms
from django.contrib.auth.models import User

_control = {"class": "form-control"}
_control_lg = {"class": "form-control form-control-lg"}


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs=_control_lg))
    password = forms.CharField(widget=forms.PasswordInput(attrs=_control_lg))


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs=_control_lg))
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs=_control_lg),
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs=_control_lg),
            "email": forms.EmailInput(attrs=_control_lg),
        }

    def clean(self):
        cleaned = super().clean()
        p = cleaned.get("password")
        pc = cleaned.get("password_confirm")
        if p and pc and p != pc:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
