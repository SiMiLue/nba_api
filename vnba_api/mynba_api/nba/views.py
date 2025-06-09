from django.shortcuts import render
from nba_api.stats.endpoints import (
    playercareerstats,
    playerdashboardbyyearoveryear, # <-- 已經導入，現在用於場均數據
    shotchartdetail,
    playergamelog,
)
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static import players, teams
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import io
import base64


def get_json_from_name(name: str, is_player=True) -> dict:
    if is_player:
        nba_players = players.get_players()
        result = [player for player in nba_players if player['full_name'] == name]
        return result[0] if result else None
    else:
        nba_teams = teams.get_teams()
        result = [team for team in nba_teams if team['full_name'] == name]
        return result[0] if result else None

def get_player_career(player_id: int) -> pd.DataFrame:
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    return career.get_data_frames()[0]

def get_shot_data(player_id: int, team_ids: list, seasons: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for season in seasons:
        for team_id in team_ids:
            shot_data = shotchartdetail.ShotChartDetail(
                team_id=team_id,
                player_id=player_id,
                context_measure_simple='FGA',
                season_nullable=season
            )
            data_frames = shot_data.get_data_frames()
            if data_frames:
                df = pd.concat([df, data_frames[0]])
    return df

def create_court(ax: mpl.axes.Axes, color="white") -> mpl.axes.Axes:
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))
    ax.plot([-250, 250], [0, 0], linewidth=4, color='black')
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    return ax

def shot_chart(df: pd.DataFrame, name: str, season=None, RA=True, extent=(-250, 250, 0, 470),
                gridsize=25, cmap="Reds"):
    fig = plt.figure(figsize=(3.6, 3.6), facecolor='white', edgecolor='white', dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], facecolor='white')
    
    if RA == True:
            x = df.LOC_X
            y = df.LOC_Y + 60
            plt.text(-240, 430, f"{name}", fontsize=21, color='black')
            if season:
                season_str = f"NBA {season[0][:4]}-{season[-1][-2:]}" if len(season) > 1 else f"NBA {season[0][:4]}-{str(int(season[0][:4]) + 1)[-2:]}"
                plt.text(-250, -20, season_str, fontsize=8, color='black')
            plt.text(110, -20, '@codegym_tech', fontsize=8, color='black')
    else:
            cond = ~((-45 < df.LOC_X) & (df.LOC_X < 45) & (-40 < df.LOC_Y) & (df.LOC_Y < 45))
            x = df.LOC_X[cond]
            y = df.LOC_Y[cond] + 60
            plt.text(-240, 430, f"{name}", fontsize=21, color='black')
            plt.text(-240, 400, "(Remove Restricted Area)", fontsize=10, color='red')
            if season:
                season_str = f"NBA {season[0][:4]}-{season[-1][-2:]}" if len(season) > 1 else f"NBA {season[0][:4]}-{str(int(season[0][:4]) + 1)[-2:]}"
                plt.text(-250, -20, season_str, fontsize=8, color='black')
            plt.text(110, -20, '@codegym_tech', fontsize=8, color='black')

    hexbin = ax.hexbin(x, y, cmap=cmap,
            bins="log", gridsize=25, mincnt=2, extent=extent) # 使用傳入的 extent

    ax = create_court(ax, 'black')                

    return fig


def home(request):

    player_id = '1628983' # Shai Gilgeous-Alexander ID

    # 1. 獲取球員生涯數據
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_totals_df = career_stats.get_data_frames()[0]

    # 2. 獲取球員基本信息
    player_info = CommonPlayerInfo(player_id=player_id)
    player_profile_df = player_info.get_data_frames()[0]

    player_details = {
        'full_name': player_profile_df['DISPLAY_FIRST_LAST'].iloc[0],
        'team_name': player_profile_df['TEAM_NAME'].iloc[0],
        'team_id': player_profile_df['TEAM_ID'].iloc[0],
        'position': player_profile_df['POSITION'].iloc[0],
        'height': player_profile_df['HEIGHT'].iloc[0],
        'weight': player_profile_df['WEIGHT'].iloc[0],
        'birthdate': player_profile_df['BIRTHDATE'].iloc[0],
        'country': player_profile_df['COUNTRY'].iloc[0],
        'draft_year': player_profile_df['DRAFT_YEAR'].iloc[0],
        'draft_round': player_profile_df['DRAFT_ROUND'].iloc[0],
        'draft_number': player_profile_df['DRAFT_NUMBER'].iloc[0],
        'last_attended': player_profile_df['SCHOOL'].iloc[0],
        'season_experience': player_profile_df['SEASON_EXP'].iloc[0],
        'jersey_number': player_profile_df['JERSEY'].iloc[0],
    }

    # 獲取球員頭貼 URL
    player_headshot_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

    # 3. 獲取按賽季的分項數據 (Year-Over-Year) - 從這裡提取場均數據
    yoy_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=player_id)
    yoy_df = yoy_stats.get_data_frames()[0]

    # 提取最新賽季的場均數據
    # 確保 yoy_df 不為空
    per_game_stats = {}
    if not yoy_df.empty:
        # 獲取最新賽季的數據 (假設是最後一行)
        latest_season_stats = yoy_df.iloc[-1]
        
        # 獲取出場次數
        gp = latest_season_stats.get('GP', 0) # 獲取 GP，如果沒有則設為 0
        
        # 計算場均數據
        if gp > 0:
            # 獲取計算 TS% 所需的基礎數據
            pts = latest_season_stats.get('PTS', 0)
            fga = latest_season_stats.get('FGA', 0)
            fta = latest_season_stats.get('FTA', 0)

            # 計算 TS%
            ts_pct = 'N/A'
            if (2 * (fga + 0.44 * fta)) > 0:
                ts_pct_value = pts / (2 * (fga + 0.44 * fta))
                ts_pct = f"{round(ts_pct_value * 100, 1)}%"

            per_game_stats = {
                'pts': round(pts / gp, 1) if 'PTS' in latest_season_stats else 'N/A',
                'reb': round(latest_season_stats.get('REB', 0) / gp, 1) if 'REB' in latest_season_stats else 'N/A',
                'ast': round(latest_season_stats.get('AST', 0) / gp, 1) if 'AST' in latest_season_stats else 'N/A',
                'stl': round(latest_season_stats.get('STL', 0) / gp, 1) if 'STL' in latest_season_stats else 'N/A',
                'blk': round(latest_season_stats.get('BLK', 0) / gp, 1) if 'BLK' in latest_season_stats else 'N/A',
                'mpg': round(latest_season_stats.get('MIN', 0) / gp, 1) if 'MIN' in latest_season_stats else 'N/A',
                'fg_pct': f"{round(latest_season_stats.get('FG_PCT', 0) * 100, 1)}%" if 'FG_PCT' in latest_season_stats else 'N/A',
                'three_p_pct': f"{round(latest_season_stats.get('FG3_PCT', 0) * 100, 1)}%" if 'FG3_PCT' in latest_season_stats else 'N/A',
                'ft_pct': f"{round(latest_season_stats.get('FT_PCT', 0) * 100, 1)}%" if 'FT_PCT' in latest_season_stats else 'N/A',
                'ts_pct': ts_pct, # 現在使用計算出的 TS%
            }
        else:
            # 如果 GP 為 0，則所有數據都設置為 N/A
            per_game_stats = {
                'pts': 'N/A', 'reb': 'N/A', 'ast': 'N/A', 'stl': 'N/A', 'blk': 'N/A',
                'mpg': 'N/A', 'fg_pct': 'N/A', 'three_p_pct': 'N/A', 'ft_pct': 'N/A', 'ts_pct': 'N/A'
            }
    else:
        # 如果沒有數據，所有統計數據都設置為 N/A
        per_game_stats = {
            'pts': 'N/A', 'reb': 'N/A', 'ast': 'N/A', 'stl': 'N/A', 'blk': 'N/A',
            'mpg': 'N/A', 'fg_pct': 'N/A', 'three_p_pct': 'N/A', 'ft_pct': 'N/A', 'ts_pct': 'N/A'
        }


    # 4. 獲取今天的比賽記分板數據
    today_scoreboard = scoreboard.ScoreBoard()
    scoreboard_data = today_scoreboard.get_dict()
    games_df = pd.DataFrame(scoreboard_data['scoreboard']['games'])

    # 5. 獲取最近比賽日誌 (PlayerGameLog)
    # 選擇最新的幾個賽季，或者只獲取最新的賽季來簡化
    current_season = '2023-24' # 根據實際情況調整
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=current_season)
    player_gamelog_df = gamelog.get_data_frames()[0]
    latest_games_df = player_gamelog_df.head(5) # 獲取最近5場比賽

    # 6. 獲取投籃數據並生成圖表
    seasons_for_shot_chart = [current_season] # 假設只顯示當前賽季的投籃圖
    team_ids_for_shot_chart = [player_details['team_id']]

    player_shots_df = get_shot_data(player_id, team_ids_for_shot_chart, seasons_for_shot_chart)

    shot_chart_fig = shot_chart(player_shots_df, player_details['full_name'], season=seasons_for_shot_chart)

    # 將圖表轉換為 Base64 編碼的圖片字符串
    buf = io.BytesIO()
    shot_chart_fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    shot_chart_image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(shot_chart_fig)

    context = {
        'player_id': player_id,
        'player_name': player_details['full_name'],
        'player_details': player_details,
        'player_headshot_url': player_headshot_url,
        'per_game_stats': per_game_stats,
        'career_totals_html': career_totals_df.to_html(classes='table table-striped'),
        'year_over_year_stats': yoy_df.to_html(classes='table table-striped'),
        'games_data': games_df.to_html(classes='table table-striped'),
        'latest_games_html': latest_games_df.to_html(classes='table table-striped', index=False),
        'shot_chart_image': shot_chart_image_base64,
    }

    return render(request, 'home.html', context)