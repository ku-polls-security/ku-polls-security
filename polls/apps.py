"""
Django application configuration for the Polls app.

This module contains the application configuration class `PollsConfig`
for the Polls application, which sets the default primary key field type
and the application name.
"""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """
    Configuration class for the Polls application.

    This class sets the application name and the default
    auto field type used for primary keys.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
