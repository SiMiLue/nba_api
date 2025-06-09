import asyncio
import time
from asgiref.sync import sync_to_async
from .service import team_slug_mapping
from django.shortcuts import render
from .service import get_team_info, fetch_team_roster
from django.utils.text import slugify
from nba_api.stats.static import teams as nba_teams
# from nba_api.stats.endpoints import teaminfocommon

from collections import defaultdict
import pprint

def teams_by_division(request):
    all_teams = nba_teams.get_teams()
    divisions = defaultdict(list)

    for team in all_teams:
        team_id = team['id']
        team['logo_url'] = f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"
        division = DIVISION_MAP.get(team_id, 'Unknown')

        divisions[division].append(team)
        # pprint(team)
        pprint.pprint(dict(divisions))  # 印出 divisions 的內容

    print("載入分區數量：", len(divisions))
    print("分區名稱：", divisions.keys())

    return render(request, "teams/DivideTeam.html", {"divisions": dict(divisions)})

def team_list(request):
    all_teams = nba_teams.get_teams()

    for team in all_teams:
        team['logo_url'] = f"https://cdn.nba.com/logos/nba/{team['id']}/global/L/logo.svg"
        team['slug'] = team_slug_mapping.get(team['full_name'], '')  # 'Rockets' → 'rockets'

    return render(request, "teams/Team.html", {"teams": all_teams})

def team_detail(request, id):
    all_teams = nba_teams.get_teams()
    team = next((t for t in all_teams if t["id"] == id), None)
    return render(request, "teams/TeamDetail.html", {"team": team})

from django.http import JsonResponse
import asyncio
from django.shortcuts import render
from .service import fetch_team_roster, get_team_info

async def team_roster(request, team_slug):
    """根據球隊 URL slug 顯示球員名單（分批載入，支援異步視圖）"""
    offset = int(request.GET.get('offset', 0))
    team_info = get_team_info(team_slug)
    team_id = team_info['id']

    if not team_info:
        return JsonResponse({'error': f"Team {team_slug} not found", 'players': []})

    players = await fetch_team_roster(team_slug, offset)  # 使用 `await` 來執行異步請求

    # 判斷是 API 請求還是 HTML 渲染
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # 判斷是否為 AJAX 請求
        return JsonResponse({'players': players})

    return render(request, 'teams/TeamRoster.html', {'team_slug': team_slug,'team_id': team_id, 'players': players})


DIVISION_MAP = {
    # Atlantic Division
    1610612738: 'Atlantic',  # Boston Celtics
    1610612751: 'Atlantic',  # Brooklyn Nets
    1610612752: 'Atlantic',  # New York Knicks
    1610612755: 'Atlantic',  # Philadelphia 76ers
    1610612761: 'Atlantic',  # Toronto Raptors

    # Central Division
    1610612739: 'Central',   # Cleveland Cavaliers
    1610612741: 'Central',   # Chicago Bulls
    1610612749: 'Central',   # Milwaukee Bucks
    1610612754: 'Central',   # Indiana Pacers
    1610612765: 'Central',   # Detroit Pistons

    # Southeast Division
    1610612737: 'Southeast', # Atlanta Hawks
    1610612748: 'Southeast', # Miami Heat
    1610612753: 'Southeast', # Orlando Magic
    1610612764: 'Southeast', # Washington Wizards
    1610612766: 'Southeast', # Charlotte Hornets

    # Northwest Division
    1610612743: 'Northwest', # Denver Nuggets
    1610612750: 'Northwest', # Minnesota Timberwolves
    1610612760: 'Northwest', # Oklahoma City Thunder
    1610612762: 'Northwest', # Utah Jazz
    1610612757: 'Northwest', # Portland Trail Blazers

    # Pacific Division
    1610612744: 'Pacific',   # Golden State Warriors
    1610612746: 'Pacific',   # LA Clippers
    1610612747: 'Pacific',   # Los Angeles Lakers
    1610612756: 'Pacific',   # Phoenix Suns
    1610612758: 'Pacific',   # Sacramento Kings

    # Southwest Division
    1610612742: 'Southwest', # Dallas Mavericks
    1610612745: 'Southwest', # Houston Rockets
    1610612740: 'Southwest', # New Orleans Pelicans
    1610612763: 'Southwest', # Memphis Grizzlies
    1610612759: 'Southwest', # San Antonio Spurs
}