import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from nba_api.stats.static import *
import joblib
all_games=pd.read_csv('C:/Users/poyan/Desktop/nba_api/vnba_api/allboxscore2020~2025.csv')
all_games['GAME_DATE'] = pd.to_datetime(all_games['GAME_DATE'])
all_games['WIN'] = all_games['WL'].apply(lambda x: 1 if x == 'W' else 0)
all_games['PTS'] = all_games['PTS'].astype(float)
all_games['PPG'] = all_games.groupby('TEAM_ID')['PTS'].transform('mean')
nba_teams = teams.get_teams()
team_abbr_to_id = {team['abbreviation']: team['id'] for team in nba_teams}


def get_opponent_team_id(matchup, team_abbr_to_id, team_id):
    if '@' in matchup:
        opponent_abbr = matchup.split(' @ ')[-1]
    else:
        opponent_abbr = matchup.split(' vs. ')[-1]
    return team_abbr_to_id.get(opponent_abbr, team_id)
all_games['OPPONENT_TEAM_ID'] = all_games.apply(
    lambda row: get_opponent_team_id(row['MATCHUP'], team_abbr_to_id, row['TEAM_ID']), axis=1
)

all_games['HOME_GAME'] = all_games['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)
all_games['LAST_GAME_RESULT'] = all_games.groupby('TEAM_ID')['WIN'].shift(1).fillna(0)

le = LabelEncoder()
all_games['TEAM_ID'] = le.fit_transform(all_games['TEAM_ID'])
all_games['OPPONENT_TEAM_ID'] = le.transform(all_games['OPPONENT_TEAM_ID'])

#train
X = all_games[['FG_PCT','FG3_PCT','FT_PCT','OREB','DREB','REB','AST','STL','BLK','TOV','PF','TEAM_ID', 'OPPONENT_TEAM_ID', 'PPG', 'HOME_GAME', 'LAST_GAME_RESULT']]
y = all_games['WIN']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)

model.fit(X_train, y_train)

y_pred= model.predict(X_test)
print("ACC:", accuracy_score(y_test, y_pred))

feature_importance = pd.DataFrame(model.feature_importances_,
                                  index = X_train.columns,
                                  columns=['importance']).sort_values('importance', ascending=False)
print("Feature_importance:\n", feature_importance)

joblib.dump(model, 'basketball_predict.pkl')
'''
team_abbr = 'LAL'
opponent_abbr = 'BOS'
average_points_per_game = 110.5

new_data = pd.DataFrame({
    'TEAM_ID': [le.transform([team_abbr_to_id[team_abbr]])[0]],
    'OPPONENT_TEAM_ID': [le.transform([team_abbr_to_id[opponent_abbr]])[0]],
    'PPG': [average_points_per_game],
    'HOME_GAME': [1],
    'LAST_GAME_RESULT': [1]
})

predictions = model.predict(new_data)
prediction_probabilities = model.predict_proba(new_data)

print("Predictions: ", predictions)
print("Prediction Probabilities: ", prediction_probabilities)
'''