from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from unittest.mock import patch


class AuthSystemTests(TestCase):

    @patch('captcha.fields.CaptchaField.clean')  # Correct the patch to the simple-captcha field
    def test_signup_successful(self, mock_captcha):
        """Test that a user can sign up successfully with valid data."""

        # Mock the CAPTCHA validation to return a valid response
        mock_captcha.return_value = None

        response = self.client.post(reverse('polls:signup'), {
            'username': 'testuser',
            'password1': 'ValidPassword1!',
            'password2': 'ValidPassword1!',
            'captcha': 'valid-captcha-response'  # Simulate a valid CAPTCHA response
        })

        # Debugging: Check if response is a redirect (302)
        print(response.status_code)
        print(response.content)

        # Check redirection to the index page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:index'))

        # Check that the user was created
        user = get_user_model().objects.filter(username='testuser').first()
        self.assertIsNotNone(user)

        # Check user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_signup_password_validation_failure(self):
        """Test that invalid passwords are rejected by the signup form."""
        response = self.client.post(reverse('polls:signup'), {
            'username': 'testuser',
            'password1': 'invalid1.',  # Invalid password (no uppercase, digit, or special char)
            'password2': 'invalid1.'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password must contain at least one uppercase letter.")

        # Check that the user was not created
        user = get_user_model().objects.filter(username='testuser').first()
        self.assertIsNone(user)

    def test_signup_mismatched_passwords(self):
        """Test that mismatched passwords are rejected."""
        response = self.client.post(reverse('polls:signup'), {
            'username': 'testuser',
            'password1': 'ValidPassword1!',
            'password2': 'DifferentPassword1!'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")

        # Check that the user was not created
        user = get_user_model().objects.filter(username='testuser').first()
        self.assertIsNone(user)

    def test_signup_duplicate_username(self):
        """Test that a duplicate username is rejected."""
        # Create an existing user
        User.objects.create_user(username='testuser', password='ValidPassword1!')

        response = self.client.post(reverse('polls:signup'), {
            'username': 'testuser',
            'password1': 'AnotherValidPassword1!',
            'password2': 'AnotherValidPassword1!'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.")

        # Check that no new user was created
        users = get_user_model().objects.filter(username='testuser')
        self.assertEqual(users.count(), 1)

    def test_signup_blank_fields(self):
        """Test that blank fields are rejected."""
        response = self.client.post(reverse('polls:signup'), {
            'username': '',
            'password1': '',
            'password2': ''
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

        # Check that the user was not created
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 0)

    def test_axes_lockout(self):
        # Create a user for testing
        user = get_user_model().objects.create_user(username='testuser', password='ValidPassword1!')
        print(f"User {user.username} created successfully")

        # Simulate multiple failed login attempts
        for _ in range(5):
            response = self.client.post(reverse('login'), {
                'username': 'testuser',
                'password': 'InvalidPassword!'  # Incorrect password
            })
            print(f"Failed login attempt response: {response.status_code}, {response.content[:100]}")

        # After 5 failed attempts, Axes should lock the user out.
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'ValidPassword1!'  # Correct password
        })
        print(f"Response after lockout attempt: {response.status_code}, {response.content[:100]}")

        # Verify that the response is a 403 Forbidden due to lockout
        self.assertEqual(response.status_code, 403)  # Expecting 403 due to lockout

        # Check for lockout message, but adjust since it's a 403 Forbidden response.
        # You might want to check the actual content in the response body.
        self.assertIn(b"Account locked: too many login attempts", response.content)
