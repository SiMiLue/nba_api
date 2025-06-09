app_name = 'teams'  # 設定命名空間
from django.urls import path
from . import views

urlpatterns = [
    path('<int:team_id>/teams-traditional', views.team_players, name='team_players'),
]