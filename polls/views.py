"""Handles poll display, voting, and admin functions in the KU Polls app."""
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Question


def index(request):
    """Determine the view of the index page."""
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """
    Determine the view of the question page.

    Catch the error if the question is not found.
    """
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """Determine the view of the result page."""
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    """Determine the view of the vote page."""
    return HttpResponse("You're voting on question %s." % question_id)
