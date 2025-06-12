"""
URL configuration for mynba_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from nba import views  # ✅ 改這裡（從 nba 匯入 views）


urlpatterns = [
    path('admin/', admin.site.urls),
    path('player_details/<int:player_id>/', views.home, name='home'),  # 頁面首頁
    path('team/', include('teams.urls')),
    path('teams/', include('players.urls')),
    path('nba_today/', include('nba_today.urls'))
]

