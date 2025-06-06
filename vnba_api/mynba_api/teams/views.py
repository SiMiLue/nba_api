from nba_api.stats.static import teams as nba_teams
# from nba_api.stats.static import teams
# from nba_api.stats.endpoints import teaminfocommon
from collections import defaultdict
from django.shortcuts import render
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

    return render(request, "teams/Team.html", {"teams": all_teams})


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
