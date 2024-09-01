"""Handles poll display, voting, and admin functions in the KU Polls app."""
from typing import Any
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Choice, Question


class IndexView(generic.ListView):
    """Determine the view of the index page."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions.

        (not including those set to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    Determine the view of the question page.

    Catch the error if the question is not found.
    """

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Handle GET requests."""
        self.object = self.get_object()
        if not self.object.is_published():
            messages.error(request, "This poll is not published yet.")
            return redirect('polls:index')
        if not self.object.can_vote():
            messages.error(request, "This poll is not allowed for voting.")
            return redirect('polls:index')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ResultsView(generic.DetailView):
    """Determine the view of the result page."""

    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """Determine the view of the vote page.

    Catch the error in the case where the choice does not exist.
    Receive the answer, then redirect to the result page.
    """
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "This poll is not allowed for voting.",
        })
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(
            reverse('polls:results', args=(question.id,))
        )
