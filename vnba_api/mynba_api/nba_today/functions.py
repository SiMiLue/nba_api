from nba_api.live.nba.endpoints import scoreboard
import pprint
import requests
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo


# get today's game scores
def get_scores():
    # Today's Score Board
    games = scoreboard.ScoreBoard()
    results = scoreboard.ScoreBoard().games.get_dict()

    return results


def get_team_image(team_id, team_name):
    #   Check for team image in database
   return f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"


def get_player_image(player_id):
 return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"