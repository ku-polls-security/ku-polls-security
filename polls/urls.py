"""Defines URL patterns for the KU Polls application."""
from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<uuid:pk>/', views.DetailView.as_view(), name='detail'),
    path('<uuid:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<uuid:question_id>/vote/', views.vote, name='vote'),
    path('signup/', views.signup, name='signup'),
    path('change_username/', views.change_username, name='change_username'),
    path('change_password/', views.change_password, name='change_password'),
    path('user_manage/', views.user_manage, name='user_manage'),
]
