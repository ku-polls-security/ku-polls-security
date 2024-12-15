"""
This module contains middleware for logging unhandled exceptions in the application.

It centralizes error logging by capturing exceptions and logging detailed error messages
along with stack traces to a logging system.
"""

import logging

# Set up logger
logger = logging.getLogger('polls')


class LogErrorMiddleware:
    """
    Middleware that logs unhandled exceptions for centralized error tracking.

    Logs the exception details along with stack trace to a logging system.
    """

    def __init__(self, get_response):
        """Init the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Call the request and response cycle."""
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Log the exception if an error occurs during the request/response cycle."""
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
