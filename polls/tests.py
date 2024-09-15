"""Contains test cases for the KU Polls application models and views."""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

from .models import Question, Choice, Vote


class QuestionModelTests(TestCase):
    """Test The Model."""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_question(self):
        """is_published() should return False for questions with a future pub_date."""
        future_question = create_question(
            question_text="Future question.", days=5
            )
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """is_published() should return True for questions with the default pub_date (now)."""
        question = create_question(
            question_text="Default pub_date question.", days=0
            )
        self.assertIs(question.is_published(), True)

    def test_is_published_with_past_question(self):
        """is_published() should return True for questions with a past pub_date."""
        past_question = create_question(
            question_text="Past question.", days=-5
            )
        self.assertIs(past_question.is_published(), True)

    def test_cannot_vote_before_pub_date(self):
        """Cannot vote if the pub_date is in the future."""
        future_question = create_question(
            question_text="Future question.", days=5
            )
        future_question.end_date = timezone.now() + datetime.timedelta(days=10)
        future_question.save()
        self.assertIs(future_question.can_vote(), False)

    def test_can_vote_within_voting_period(self):
        """Can vote if the current time is between pub_date and end_date."""
        question = create_question(
            question_text="Active voting period question.", days=-1
            )
        question.end_date = timezone.now() + datetime.timedelta(days=5)
        question.save()
        self.assertIs(question.can_vote(), True)

    def test_cannot_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        question = create_question(
            question_text="Ended voting period question.", days=-10
            )
        question.end_date = timezone.now() - datetime.timedelta(days=5)
        question.save()
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_no_end_date(self):
        """Voting is allowed if there is no end_date specified."""
        question = create_question(
            question_text="No end date question.", days=-1
            )
        question.end_date = None  # No end date specified
        question.save()
        self.assertIs(question.can_vote(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """Test The Index View."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']), [question]
            )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']), [question]
            )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question2, question1]
        )


class QuestionDetailViewTests(TestCase):
    """Test The Detail View."""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302.
        """
        future_question = create_question(
            question_text='Future question.', days=5
        )
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
            question_text='Past Question.', days=-5
        )
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteViewTests(TestCase):
    """Test the voting view for the KU Polls application."""

    def setUp(self):
        """Set up the initial data for the tests."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.question = create_question(question_text="Sample Question", days=-1)
        self.choice = Choice.objects.create(question=self.question, choice_text="Choice 1")

    def test_vote_success(self):
        """Test that a valid vote is recorded and redirected to results."""
        self.client.login(username='testuser', password='12345')
        url = reverse('polls:vote', args=(self.question.id,))
        response = self.client.post(url, {'choice': self.choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().choice, self.choice)

    def test_vote_after_end_date(self):
        """Attempting to vote after the question's end_date should fail."""
        past_question = create_question(question_text="Past Question", days=-10)
        past_question.end_date = timezone.now() - timezone.timedelta(days=1)
        past_question.save()
        url = reverse('polls:vote', args=(past_question.id,))
        self.client.login(username='testuser', password='12345')
        response = self.client.post(url, {'choice': self.choice.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This poll is not allowed for voting.")

    def test_user_cannot_vote_multiple_times(self):
        """A user should not be able to vote multiple times for the same question."""
        self.client.login(username='testuser', password='12345')
        url = reverse('polls:vote', args=(self.question.id,))
        self.client.post(url, {'choice': self.choice.id})
        response = self.client.post(url, {'choice': self.choice.id})
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(Vote.objects.count(), 1)  # User should only have one vote for this question
