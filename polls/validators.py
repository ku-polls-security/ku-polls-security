from django.core.exceptions import ValidationError
import re
import hashlib
import requests

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        # Check for digit
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")

        # Check for compromised password
        sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_password[:5], sha1_password[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)

        if response.status_code != 200:
            raise ValidationError(
                "Could not validate the password against compromised databases. Please try again later."
            )

        if suffix in response.text:
            raise ValidationError("This password has been compromised and cannot be used.")

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, one special character, and "
            "must not be a known compromised password."
        )
