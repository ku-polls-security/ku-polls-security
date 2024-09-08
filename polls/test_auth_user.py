"""Tests of authentication."""
import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from polls.models import Question, Choice
from django.conf import settings

class UserAuthTest(django.test.TestCase):

    def setUp(self):
        # Initialize the test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()

        # Create a poll question and choices
        q = Question.objects.create(question_text="First Poll Question")
        for n in range(1, 4):
            Choice.objects.create(choice_text=f"Choice {n}", question=q)
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url."""
        logout_url = reverse("logout")
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # Use POST to logout, as many logout implementations expect POST
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        # Login using a POST request
        form_data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(login_url, form_data)
        self.assertEqual(response.status_code, 302)

        # Redirect to the polls index page or custom URL
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        form_data = {"choice": str(choice.id)}
        response = self.client.post(vote_url, form_data)

        # Should redirect to the login page with next parameter
        self.assertEqual(response.status_code, 302)
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)
