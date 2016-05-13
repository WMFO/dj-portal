from django import forms

class LoginForm(forms.Form):
    email_address = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
