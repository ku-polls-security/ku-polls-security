"""Tell the admin that Question objects have an admin interface."""
from django.contrib import admin

from .models import Question, Choice

admin.site.register(Question)
admin.site.register(Choice)
