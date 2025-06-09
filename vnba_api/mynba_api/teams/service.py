import asyncio
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamplayerdashboard
from django.core.cache import cache
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo

# 球隊名稱與 NBA 官方網站 URL slug 對應表
team_slug_mapping = {
    "Atlanta Hawks": "hawks",
    "Boston Celtics": "celtics",
    "Brooklyn Nets": "nets",
    "Charlotte Hornets": "hornets",
    "Chicago Bulls": "bulls",
    "Cleveland Cavaliers": "cavaliers",
    "Dallas Mavericks": "mavericks",
    "Denver Nuggets": "nuggets",
    "Detroit Pistons": "pistons",
    "Golden State Warriors": "warriors",
    "Houston Rockets": "rockets",
    "Indiana Pacers": "pacers",
    "LA Clippers": "clippers",
    "Los Angeles Lakers": "lakers",
    "Memphis Grizzlies": "grizzlies",
    "Miami Heat": "heat",
    "Milwaukee Bucks": "bucks",
    "Minnesota Timberwolves": "timberwolves",
    "New Orleans Pelicans": "pelicans",
    "New York Knicks": "knicks",
    "Oklahoma City Thunder": "thunder",
    "Orlando Magic": "magic",
    "Philadelphia 76ers": "sixers",
    "Phoenix Suns": "suns",
    "Portland Trail Blazers": "blazers",
    "Sacramento Kings": "kings",
    "San Antonio Spurs": "spurs",
    "Toronto Raptors": "raptors",
    "Utah Jazz": "jazz",
    "Washington Wizards": "wizards"
}

def get_team_info(team_slug):
    """根據球隊 URL slug 獲取球隊資訊"""
    cache_key = f"team_info_{team_slug}"
    team_info = cache.get(cache_key)

    if not team_info:
        team_name = next((name for name, slug in team_slug_mapping.items() if slug == team_slug), None)
        if not team_name:
            return None

        team_info = next((team for team in teams.get_teams() if team['full_name'] == team_name), None)
        cache.set(cache_key, team_info, timeout=600)

    return team_info

async def fetch_player_info(player_id):
    """使用 Asyncio 並行請求 NBA API 獲取球員背號與圖片"""
    cache_key = f"player_info_{player_id}"
    player_data = cache.get(cache_key)

    if player_data:
        return player_data

    try:
        info = CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
        player_data = {
            'id': player_id,
            'name': info.get("DISPLAY_FIRST_LAST", ["Unknown Player"])[0],
            'jersey': info.get("JERSEY", ["N/A"])[0],
            'headshot_url': f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
        }
    except Exception as e:
        print(f"⚠️ 無法獲取球員資料 (ID: {player_id}) - {str(e)}")
        player_data = {'id': player_id, 'jersey': "N/A", 'headshot_url': "/static/default_player.png"}

    cache.set(cache_key, player_data, timeout=600)
    return player_data

async def fetch_team_roster(team_slug, offset=0, batch_size=6):
    """分批載入球隊球員，每次抓取 6 位"""
    team_info = get_team_info(team_slug)
    if not team_info:
        return []

    team_id = team_info['id']
    cache_key = f"team_roster_{team_id}_{offset}"
    cached_roster = cache.get(cache_key)

    if cached_roster:
        return cached_roster

    try:
        player_stats = teamplayerdashboard.TeamPlayerDashboard(team_id=team_id)
        players_data = player_stats.get_data_frames()[1].iloc[offset:offset + batch_size]
    except Exception as e:
        print(f"⚠️ 球隊數據請求失敗 (Team ID: {team_id}) - {str(e)}")
        return []

    tasks = [fetch_player_info(player['PLAYER_ID']) for _, player in players_data.iterrows()]
    results = await asyncio.gather(*tasks)

    cache.set(cache_key, results, timeout=600)
    return results