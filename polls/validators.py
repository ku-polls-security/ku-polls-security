"""
Custom password validator to enforce strong policies.

Prevent compromised use.
"""

import re
import hashlib
import requests
import logging
from django.core.exceptions import ValidationError

# Set up logging
logger = logging.getLogger(__name__)


class CustomPasswordValidator:
    """
    Validator for enforcing strong password policies.

    Avoiding compromises.
    """

    def validate(self, password, user=None):
        """
        Validate strong password.

        Checks against compromised.
        """
        logger.debug("Validating password for compliance.")

        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            logger.warning("Password missing an uppercase letter.")
            raise ValidationError(
                "Password must contain at least one uppercase letter."
                )

        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            logger.warning("Password missing a lowercase letter.")
            raise ValidationError(
                "Password must contain at least one lowercase letter."
                )

        # Check for digit
        if not re.search(r'\d', password):
            logger.warning("Password missing a digit.")
            raise ValidationError("Password must contain at least one digit.")

        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            logger.warning("Password missing a special character.")
            raise ValidationError(
                "Password must contain at least one special character."
                )

        # Check for compromised password
        logger.debug(
            "Checking password against the Have I Been Pwned database."
            )
        sha1_password = hashlib.sha1(
            password.encode('utf-8')
            ).hexdigest().upper()
        prefix, suffix = sha1_password[:5], sha1_password[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)

        if response.status_code != 200:
            logger.error("Failed to connect to the Have I Been Pwned API.")
            raise ValidationError(
                "Could not validate the password against compromised"
                "databases. Please try again later."
            )

        if suffix in response.text:
            logger.warning("Password found in compromised password database.")
            raise ValidationError(
                "This password has been compromised and cannot be used."
                )

        logger.info("Password successfully validated.")

    def get_help_text(self):
        """Return password requirement details."""
        return (
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, one special character, and "
            "must not be a known compromised password."
        )
