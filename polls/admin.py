"""Tell the admin that Question objects have an admin interface."""
from django.contrib import admin

from .models import Question

admin.site.register(Question)
