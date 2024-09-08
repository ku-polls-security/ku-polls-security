"""Handles poll display, voting, and admin functions in the KU Polls app."""
from typing import Any
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Choice, Question, Vote


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

        # Get the user's vote for this question if it exists
        user_vote = None
        if request.user.is_authenticated:
            try:
                user_vote = Vote.objects.get(
                    user=request.user, choice_question=self.object
                    )
            except Vote.DoesNotExist:
                user_vote = None

        context = self.get_context_data(
            object=self.object, user_vote=user_vote
            )
        return self.render_to_response(context)


class ResultsView(generic.DetailView):
    """Determine the view of the result page."""

    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """Determine the view of the vote page.

    Catch the error in the case where the choice does not exist.
    Receive the answer, then redirect to the result page.
    """
    user = request.user
    print("current user is", user.id, "login", user.username)
    print("Real name:", user.first_name, user.last_name)
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        messages.error(request, "This poll is not allowed for voting.")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a choice.")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    # Reference to the current user
    this_user = request.user

    # Get the user's vote
    try:
        vote = Vote.objects.get(user=this_user, choice_question=question)
        vote.choice = selected_choice
        vote.save()
        messages.success(
            request,
            f"Your vote was changed to '{selected_choice.choice_text}'"
        )
    except Vote.DoesNotExist:
        # does not have a vote yet
        vote = Vote.objects.create(
            user=this_user, choice=selected_choice, choice_question=question
            )
        # automatically saved
        messages.success(
            request,
            f"Your voted '{selected_choice.choice_text}'"
        )

    # marks this user as having voted
    # request.session[f'has_voted_{question_id}'] = True

    return HttpResponseRedirect(
        reverse('polls:results', args=(question.id,))
    )


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
        return redirect('polls:index')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
