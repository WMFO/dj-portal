from django import forms

class CustomDateInput(forms.widgets.TextInput):
    input_type = 'date'

class RegisterForm(forms.Form):
    first_name = forms.CharField()
    middle_name = forms.CharField()
    last_name = forms.CharField()
    nick_name = forms.CharField()
    student_id = forms.CharField(help_text='Non-students enter n/a')
    email = forms.EmailField()
    date_joined = forms.DateField(widget=CustomDateInput,help_text='Approximate date you joined WMFO')
    phone = forms.CharField()
    number_of_semesters = forms.IntegerField()
    spinitron_email = forms.EmailField(help_text='Email you use to log into spinitron')
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

