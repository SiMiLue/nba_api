from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import teams as nba_teams
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamplayerdashboard
from collections import defaultdict
from django.shortcuts import render
import pprint

team_name = "boston"
team_info = next((team for team in teams.get_teams() if team['full_name'].lower() == team_name.lower()), None)
print(teams.get_teams())