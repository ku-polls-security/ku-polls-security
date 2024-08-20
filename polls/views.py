"""Handles poll display, voting, and admin functions in the KU Polls app."""
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
