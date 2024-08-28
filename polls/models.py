"""Defines the Question and Choice models for the KU Polls application."""
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """Model representing a poll question."""

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


class Choice(models.Model):
    """Model representing a choice for a specific poll question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        Return a string representation of the choice.

        Returns:
            str: The text of the choice.
        """
        return self.choice_text
