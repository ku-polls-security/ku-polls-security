"""Handles poll display, voting, and admin functions in the KU Polls app."""
from typing import Any
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
    Http404,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from .forms import UsernameChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomSignupForm

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

    def get_object(self, queryset=None):
        """
        Override get_object to handle non-existing questions.

        If the question doesn't exist,
        redirect to the index page with a message.
        """
        try:
            return super().get_object(queryset)
        except Http404 as e:
            logger.error(f"Question not found: {e}")
            messages.error(
                self.request, "The poll you are looking for does not exist."
                )
            return None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Handle GET requests."""
        self.object = self.get_object()
        if self.object is None:
            return redirect('polls:index')
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

    def get_object(self, queryset=None):
        """
        Override get_object to handle non-existing questions.

        If the question doesn't exist,
        redirect to the index page with a message.
        """
        try:
            return super().get_object(queryset)
        except Http404 as e:
            logger.error(f"Question not found: {e}")
            messages.error(
                self.request, "The poll you are looking for does not exist."
                )
            return None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Handle GET requests."""
        self.object = self.get_object()
        if self.object is None:
            return redirect('polls:index')

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# Get a logger instance
logger = logging.getLogger('polls')


@login_required
def vote(request, question_id):
    """Handle the voting process for a given question."""
    user = request.user
    ip_addr = get_client_ip(request)

    logger.info(
        f"User {user.username} voted from"
        f" IP {ip_addr} on question {question_id}"
    )

    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        logger.warning(
            f"User {user.username} tried to vote on a closed poll "
            f"{question_id}"
        )
        messages.error(request, "This poll is not allowed for voting.")
        return render(request, 'polls/detail.html', {'question': question})

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except KeyError:
        logger.warning(
            f"Choice ID not found in POST data for user {user.username}"
            )
        messages.error(request, "You didn't select a valid choice.")
        return render(request, 'polls/detail.html', {'question': question})
    except Choice.DoesNotExist:
        logger.warning(
            f"Invalid choice ID for question {question_id} "
            f"by user {user.username}"
        )
        messages.error(request, "Invalid choice selection.")
        return render(request, 'polls/detail.html', {'question': question})

    try:
        vote = Vote.objects.get(user=user, choice_question=question)
        vote.choice = selected_choice
        vote.save()
        messages.success(
            request,
            f"Your vote was changed to '{selected_choice.choice_text}'"
        )
        logger.info(
            f"User {user.username} changed their vote for question "
            f"{question_id} to '{selected_choice.choice_text}'"
        )
    except Vote.DoesNotExist:
        Vote.objects.create(
            user=user, choice=selected_choice, choice_question=question
        )
        messages.success(
            request, f"Your vote '{selected_choice.choice_text}' was recorded"
        )
        logger.info(
            f"User {user.username} voted for the first time on question "
            f"{question_id} with '{selected_choice.choice_text}'"
        )

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def consent_submission(request):
    """Return JsonResponse of consent."""
    if request.method == 'POST':
        consent = request.POST.get('consent1')
        if consent == 'yes':
            request.session['consent_given'] = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse(
                {'success': False, 'message': 'You must consent to proceed.'}
                )
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            # Save the user instance
            user = form.save()

            # Authenticate the user explicitly to determine the backend
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            if user:
                login(request, user)  # Log in the user
                messages.success(
                    request,
                    f"Account created successfully! Welcome, {user.username}!"
                )
                logger.info(f"User {user.username} login.")
                return redirect('polls:index')

            # Handle edge cases (e.g., backend misconfiguration)
            messages.error(
                request,
                "Authentication failed. Please try logging in."
            )
            logger.warning("User authentication failed.")
        else:
            messages.error(
                request,
                "There was an error with your submission. Please try again."
            )
            logger.error("Error with submission.")
    else:
        form = CustomSignupForm()
        logger.warning("Invalid form submission.")
    return render(request, 'registration/signup.html', {'form': form})


def policy(request):
    """Render policy page."""
    if request.method == 'POST':
        choice = request.POST.get('consent1', None)

        if choice == 'yes':
            # Set a session variable to track consent
            request.session['consent_given'] = True
            return redirect('signup')

        else:
            messages.info(request, "You must agree to our policy to signup!")
            logger.warning(
                "User did not agree to the policy and "
                "attempted to proceed with signup."
            )
            return redirect('signup')
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/policy.html', {'form': form})


@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    """
    Info message when a user successfully logs in.

    Args:
        sender: The model class sending the signal(typically the `User` model).
        request: The HTTP request object.
        user: The user object who logged in.
        **kwargs: Additional keyword arguments.
    """
    ip_addr = get_client_ip(request)
    logger.info(f"User {user.username} logged in from {ip_addr}")


@receiver(user_logged_out)
def log_user_logged_out(sender, request, user, **kwargs):
    """
    Info message when a user successfully logs out.

    Args:
        sender: The model class sending the signal(typically the `User` model).
        request: The HTTP request object.
        user: The user object who logged out.
        **kwargs: Additional keyword arguments.
    """
    ip_addr = get_client_ip(request)
    logger.info(f"User {user.username} logged out from {ip_addr}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Warning message whenever a login attempt fails.

    Args:
        sender: The model class sending the signal(typically the `User` model).
        credentials: The credentials provided during the failed login attempt.
        request: The HTTP request object.
        **kwargs: Additional keyword arguments.
    """
    ip_addr = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    logger.warning(f"Failed login attempt for {username} from {ip_addr}")


def get_client_ip(request):
    """
    Get the visitor’s IP address from the request headers.

    Handles scenarios where the IP address may be forwarded by proxies
    or load balancers.

    Args:
        request: The HTTP request object.

    Returns:
        str: The client's IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '').strip()
    if not ip:
        ip = '0.0.0.0'  # Fallback IP
        logger.warning("Unable to determine client IP address")
    return ip


@login_required
def change_username(request):
    """Return render change_username.html."""
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            user = request.user
            user.username = new_username
            user.save()
            messages.success(
                request, "Your username has been successfully updated."
            )
            logger.info(
                "User %s successfully updated their username.",
                user.username
                )
            return redirect('polls:index')  # Or wherever you want to redirect
        else:
            logger.warning(
                "Invalid username change attempt by user %s.",
                request.user.username
                )
    else:
        form = UsernameChangeForm()

    return render(request, 'registration/change_username.html', {'form': form})


@login_required
def change_password(request):
    """Return render change_password.html."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(
                request, "Your password was successfully updated."
            )
            logger.info(
                "User %s successfully updated their password.",
                request.user.username
                )
            return redirect('polls:index')  # Or wherever you want to redirect
        else:
            logger.warning(
                "Invalid password change attempt by user %s.",
                request.user.username
                )
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def user_manage(request):
    """Return render user_manage.html."""
    logger.info(
        "User %s accessed the user management page.",
        request.user.username
        )
    return render(request, 'registration/user_manage.html')
