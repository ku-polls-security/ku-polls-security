"""This module contains forms for user authentication and signup."""

import logging
from django import forms
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from django.contrib.auth.forms import UserCreationForm

# Set up logger
logger = logging.getLogger(__name__)


class UsernameChangeForm(forms.Form):
    """
    A form for changing the username of a user, with password validation.

    Ensures that the current password is correct before allowing a username change.
    """

    new_username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        """Initialize form and accept user as an argument."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password(self):
        """Validate that the provided password matches the current user's password."""
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            logger.warning(f"Incorrect password for user {self.user.username}")
            raise ValidationError("Incorrect password.")
        return password


class CustomSignupForm(UserCreationForm):
    """
    A custom signup form that includes a CAPTCHA field in addition to the standard.

    User creation fields for registration. This is used for preventing automated signups.
    """

    captcha = CaptchaField()

    class Meta(UserCreationForm.Meta):
        """
        Meta class for CustomSignupForm to include CAPTCHA field along with default fields.

        Inherits from UserCreationForm.Meta and adds the 'captcha' field.
        """

        fields = UserCreationForm.Meta.fields + ('captcha',)
