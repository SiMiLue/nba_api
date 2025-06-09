# teams/urls.py
from django.urls import path
from .views import team_list, teams_by_division, team_detail, team_roster

urlpatterns = [
    path('teams/', team_list, name='team-list'),
    path('teamsdivide/', teams_by_division, name='teams-by-division'),
    path('teams/<int:id>/', team_detail, name='team-detail'),
    path('<str:team_slug>/roster', team_roster, name='team-roster')
]