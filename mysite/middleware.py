import logging

logger = logging.getLogger('polls')

class LogErrorMiddleware:
    """Middleware for centralized error logging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
