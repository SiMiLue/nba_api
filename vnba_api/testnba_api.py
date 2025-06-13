from nba_api.stats.endpoints import *
from nba_api.stats.static import *
import pandas as pd
import requests

def get_nba_official_schedule():
    url = 'https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json'
    data = requests.get(url).json()
    games = []

    for game in data['leagueSchedule']['gameDates']:
        for g in game['games']:
            games.append({
                'game_date': game['gameDate'],
                'home_team': g['homeTeam']['teamTricode'],
                'away_team': g['awayTeam']['teamTricode'],
                'game_time_utc': g['gameDateTimeUTC']
            })
    for item in games:
        item['logo_url']=find_logo((item['home_team']).lower())
        item['o_logo_url']=find_logo((item['away_team']).lower())
        print(item)
    return games
def find_logo(slug):
    team_id = teams.find_team_by_abbreviation(slug)['id']
    return f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg" 
#print(get_nba_official_schedule()[-5:-1])
print(find_logo('den'))