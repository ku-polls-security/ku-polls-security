"""Defines the Question and Choice models for the KU Polls application."""
import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """Model representing a poll question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        """
        Return a string representation of the question.

        Returns:
            str: The text of the question.
        """
        return self.question_text

    def was_published_recently(self):
        """
        Determine if the question was published within the last day.

        Returns:
            bool: True if the question was published within the last day,
            False otherwise.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Determine if the question is published.

        Returns:
            bool: True if the current date-time is on or after question’s
            publication date, False otherwise.
        """
        return timezone.localtime() >= self.pub_date

    def can_vote(self):
        """
        Determine if the question can be voted on.

        Returns:
            bool: True if voting is allowed for this question,
            False otherwise.
        """
        if self.end_date:
            return self.pub_date <= timezone.localtime() < self.end_date
        return True


class Choice(models.Model):
    """Model representing a choice for a specific poll question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """Returns the votes for this choice."""
        return self.vote_set.count()

    def __str__(self):
        """
        Return a string representation of the choice.

        Returns:
            str: The text of the choice.
        """
        return self.choice_text


class Vote(models.Model):
    """Model representing a vote cast by a user for a specific choice."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    choice_question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        """
        Return a string representation of the vote.

        Returns:
            str: The text of the choice associated with the vote.
        """
        return f"{self.user.username} voted for {self.choice.choice_text}"
