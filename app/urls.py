"""
URL configuration for GamesRanking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

from app.views import (ranking_view, login_usuario, registrar_usuario, home_view, lista_juegos, crear_ranking,
                       guardar_ranking, admin_view, editar_categoria, cargar_datos, detalle_categoria,
                       eliminar_categoria,
                       elegir_categoria_ranking, valorar_juego, obtener_valoracion, mis_rankings, eliminar_ranking,
                       obtener_comentarios_juego, global_ranking, inicio,
                       sincronizar_api, supervision_admin, eliminar_juego_completo)

urlpatterns = [
    path('ranking/', ranking_view, name='ranking'),
    path('home/', home_view, name='home'),
    path('', inicio, name='login'),
    path('inicio/', inicio, name='login'),
    path('login/', login_usuario, name='login'),
    path('register/', registrar_usuario, name='register'),
    path('logout/', login_usuario, name='logout'),
    path('ver_juegos/', lista_juegos, name='ver_juegos'),
    path('crear_tierlist/', login_usuario, name='crear_tierlist'),
    path("crear_ranking/", crear_ranking, name="crear_ranking"),
    path("guardar_ranking/", guardar_ranking, name="guardar_ranking"),
    path('admin_view/', admin_view, name='admin_view'),
    path('editar_categoria/', editar_categoria, name='editar_categoria'),
    path('detalle_categoria/<str:idcat>/', detalle_categoria, name='detalle_categoria'),
    path('eliminar_categoria/<str:idcat>/', eliminar_categoria, name='eliminar_categoria'),
    path('cargar_datos/', cargar_datos, name='cargar_datos'),
    path('elegir_categoria/', elegir_categoria_ranking, name='elegir_categoria_ranking'),
    path('crear_ranking/<str:idcat>/', crear_ranking, name='crear_ranking'),
    path('valorar_juego/', valorar_juego, name='valorar_juego'),
    path('obtener_valoracion/<int:game_id>/', obtener_valoracion, name='obtener_valoracion'),
    path('mis_rankings/', mis_rankings, name='mis_rankings'),
    path('eliminar_ranking/<str:ranking_id>/', eliminar_ranking, name='eliminar_ranking'),
    path('api/comentarios/<int:game_id>/', obtener_comentarios_juego, name='obtener_comentarios_juego'),
    path('estadisticas/', global_ranking, name='ver_estadisticas'),

    # --- NUEVAS RUTAS PARA CUBRIR REQUISITOS DEL PROYECTO ---
    path('sincronizar_api/', sincronizar_api, name='sincronizar_api'),  # RF5
    path('supervision/', supervision_admin, name='supervision_admin'),  # RF10
    path('eliminar_juego/<int:game_id>/', eliminar_juego_completo, name='eliminar_juego'),  # RF4
]