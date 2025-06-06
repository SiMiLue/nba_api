from django.shortcuts import render
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players, teams # <-- 新增導入
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import io # <-- 新增導入，用於處理圖片緩衝區
import base64 # <-- 新增導入，用於圖片編碼

# 您提供的輔助函數
def get_json_from_name(name: str, is_player=True) -> dict: # 修正返回類型為 dict
    # 從 nba_api.stats.static 導入 players 和 teams (確保在函數外部已導入)
    if is_player:
        nba_players = players.get_players()
        # 注意: 這裡您可能需要處理找不到球員的情況，例如返回 None 或拋出錯誤
        result = [player for player in nba_players if player['full_name'] == name]
        return result[0] if result else None # 返回第一個匹配項或 None
    else:
        nba_teams = teams.get_teams()
        result = [team for team in nba_teams if team['full_name'] == name]
        return result[0] if result else None # 返回第一個匹配項或 None

def get_player_career(player_id: int) -> pd.DataFrame: # 修正返回類型為 pd.DataFrame
    # 從 nba_api.stats.endpoints 導入 playercareerstats (確保在函數外部已導入)
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    return career.get_data_frames()[0]

def get_shot_data(player_id: int, team_ids: list, seasons: list) -> pd.DataFrame: # 修正返回類型為 pd.DataFrame, 參數名為 player_id
    # 從 nba_api.stats.endpoints 導入 shotchartdetail (確保在函數外部已導入)
    df = pd.DataFrame()
    for season in seasons:
        for team_id in team_ids: # 確保這裡使用 team_id
            shot_data = shotchartdetail.ShotChartDetail(
                team_id=team_id,
                player_id=player_id,
                context_measure_simple='FGA', # 通常是 FGA (投籃嘗試), 而不是 PTS
                season_nullable=season
            )
            # 檢查 get_data_frames() 是否返回空列表，避免 concat 錯誤
            data_frames = shot_data.get_data_frames()
            if data_frames:
                df = pd.concat([df, data_frames[0]])

    return df

def create_court(ax: mpl.axes.Axes, color="white") -> mpl.axes.Axes: # 修正 ax 類型提示
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)
    # 3PT Arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))
    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))
    ax.plot([-250, 250], [0, 0], linewidth=4, color='black')
    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))
    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    return ax

def shot_chart(df: pd.DataFrame, name: str, season=None, RA=True, extent=(-250, 250, 422.5, -47.5),
                gridsize=25, cmap="Reds"):
    fig = plt.figure(figsize=(3.6, 3.6), facecolor='white', edgecolor='white', dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], facecolor='white')
    
    # Plot hexbin of shots
    if RA == True:
            x = df.LOC_X
            y = df.LOC_Y + 60
            # Annotate player name and season
            plt.text(-240, 430, f"{name}", fontsize=21, color='black')
            season = f"NBA {season[0][:4]}-{season[-1][-2:]}"
            plt.text(-250, -20, season, fontsize=8, color='black')
            plt.text(110, -20, '@codegym_tech', fontsize=8, color='black')
    else:
            cond = ~((-45 < df.LOC_X) & (df.LOC_X < 45) & (-40 < df.LOC_Y) & (df.LOC_Y < 45))
            x = df.LOC_X[cond]
            y = df.LOC_Y[cond] + 60
            # Annotate player name and season
            plt.text(-240, 430, f"{name}", fontsize=21, color='black')
            plt.text(-240, 400, "(Remove Restricted Area)", fontsize=10, color='red')
            season = f"NBA {season[0][:4]}-{season[-1][-2:]}"
            plt.text(-250, -20, season, fontsize=8, color='black')
            plt.text(110, -20, '@codegym_tech', fontsize=8, color='black')

    hexbin = ax.hexbin(x, y, cmap=cmap,
            bins="log", gridsize=25, mincnt=2, extent= (-250, 250, 0, 470))

    # Draw court
    ax = create_court(ax, 'black')                

    return fig

# 您的 home 視圖函數
def home(request):
    draymond_green_id = '203110'

    # 1. 獲取球員生涯數據
    career_stats = playercareerstats.PlayerCareerStats(player_id=draymond_green_id)
    draymond_career_df = career_stats.get_data_frames()[0]

    # 2. 獲取球員基本信息
    player_info = CommonPlayerInfo(player_id=draymond_green_id)
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

    # 3. 獲取按賽季的分項數據 (Year-Over-Year)
    yoy_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=draymond_green_id)
    yoy_df = yoy_stats.get_data_frames()[0]

    # 4. 獲取今天的比賽記分板數據
    today_scoreboard = scoreboard.ScoreBoard()
    scoreboard_data = today_scoreboard.get_dict()
    games_df = pd.DataFrame(scoreboard_data['scoreboard']['games'])

    # 5. 獲取投籃數據並生成圖表 (使用您提供的函數)
    # 獲取 Draymond Green 的隊伍 ID (已經在 player_details 中)
    # 我們需要一個賽季列表，例如獲取 2022-23 和 2023-24 賽季的數據
    seasons = ['2022-23', '2023-24'] # 您可以根據需要調整賽季
    team_ids = [player_details['team_id']] # 獲取當前球隊的投籃數據

    draymond_shots_df = get_shot_data(draymond_green_id, team_ids, seasons)

    # 生成 matplotlib 圖表
    shot_chart_fig = shot_chart(draymond_shots_df, player_details['full_name'], season=seasons)

    # 將圖表轉換為 Base64 編碼的圖片字符串
    buf = io.BytesIO()
    shot_chart_fig.savefig(buf, format='png', bbox_inches='tight') # 保存到緩衝區
    buf.seek(0) # 將緩衝區指針移到開頭
    shot_chart_image_base64 = base64.b64encode(buf.read()).decode('utf-8') # 編碼為 Base64
    plt.close(shot_chart_fig) # 關閉圖形，釋放記憶體

    context = {
        'player_name': player_details['full_name'],
        'player_details': player_details,
        'career_stats': draymond_career_df.to_html(classes='table table-striped'),
        'year_over_year_stats': yoy_df.to_html(classes='table table-striped'),
        'games_data': games_df.to_html(classes='table table-striped'),
        'shot_chart_image': shot_chart_image_base64, # 傳遞 Base64 編碼的圖片
    }
    return render(request, 'home.html', context)