from nba_api.stats.endpoints import *
from nba_api.stats.static import teams

import pandas as pd
import time
team_dict = teams.get_teams()
teamids = []
for item in team_dict:
    teamids.append(item['id'])

all_games=[]
error_game_id=[]
i=0
for teamid in teamids:
    print(f"Fetching advanced stats for Game ID: {teamid} ({i}/{30})")
    try:
        i=i+1
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=teamid)
        games = gamefinder.get_data_frames()[0]
        games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
        valid_games=games[games['GAME_DATE']>'2020-01-01']
        all_games.append(valid_games)
        time.sleep(0.6)
    except:
        print(f"error:{teamid}")
        error_game_id.append(teamid)
all_games_df = pd.concat(all_games, ignore_index=True)
all_games_df.to_csv('./allboxscore2020~2025.csv')
'''

all_games=[]
for season in seasons:
    gamelog = teamgamelogs.TeamGameLogs(season_nullable=season)
    df = gamelog.get_data_frames()[0]
    df['SEASON'] = season
    all_games.append(df)
    
all_games_df = pd.concat(all_games, ignore_index=True)

all_boxscores=[]
gameids=all_games_df['GAME_ID']
i=0
error_game_id=[]
for i in range(len(gameids)):
    print(f"Fetching advanced stats for Game ID: {gameids[i]} ({i}/{2430})")
    if(i%5==0):time.sleep(3)
    try:
        boxscore=boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=gameids[i]).get_data_frames()[1]
        all_boxscores.append(boxscore)
        
    except:
        print(f"error:{gameids[i]}")
        error_game_id.append(gameids[i])
print(error_game_id)
all_boxscores_df = pd.concat(all_boxscores, ignore_index=True)
all_boxscores_df.to_csv('./allboxscore2020~2025.csv')
'''


