from django import forms
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError

class UsernameChangeForm(forms.Form):
    new_username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    # Initialize form to accept user as an argument
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pop the user out of kwargs and store it
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError("Incorrect password.")
        return password
