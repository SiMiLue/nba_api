from django.shortcuts import render

# Create your views here.
import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from nba_api.stats.endpoints import commonteamroster, playercareerstats
from nba_api.stats.static import teams


def team_players(request, team_id):
    """顯示指定球隊的所有球員資料"""
    try:
        # 使用 nba_api 獲取球隊名稱
        team_info = teams.find_team_name_by_id(team_id)
        if not team_info:
            team_name = f"{team_id}"
        else:
            team_name = team_info['full_name']
        team_logo_url = f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"

        # 獲取球隊球員名單
        roster = commonteamroster.CommonTeamRoster(team_id=team_id)
        players_data = roster.get_data_frames()[0]  # 獲取球員資料

        # 轉換為字典格式方便模板使用
        players = []
        for _, player in players_data.iterrows():
            players.append({
                'name': player['PLAYER'],
                'id': player['PLAYER_ID'],
                'number': player.get('NUM', 'N/A'),
                'position': player['POSITION'],
                'height': player['HEIGHT'],
                'weight': player['WEIGHT'],
                'birth_date': player['BIRTH_DATE'],
                'age': player['AGE'],
                'experience': player['EXP'],
                'school': player['SCHOOL'],
                'how_acquired': player.get('HOW_ACQUIRED', 'Unknown')
            })

        context = {
            'team': {'id': team_id, 'name': team_name, 'logo_url': team_logo_url},
            'players': players
        }
        return render(request, 'player_list.html', context)

    except Exception as e:
        context = {
            'error': f"無法獲取球隊 {team_id} 的球員資料: {str(e)}",
            'team': {'id': team_id, 'name': f"Team {team_id}"},
            'players': []
        }
        return render(request, 'player_list.html', context)