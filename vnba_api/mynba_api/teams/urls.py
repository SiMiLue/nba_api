# teams/urls.py
from django.urls import path
from .views import team_list, teams_by_division

urlpatterns = [
    path('teams/', team_list, name='team-list'),
    path('teamsdivide/', teams_by_division, name='teams-by-division'),
]
