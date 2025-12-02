from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),   # Nova
    path('logout/', views.logout_user, name='logout_user'), # Nova
    path('perfil/', views.user_area, name='user_area'),
    path('perfil/atualizar/', views.update_user, name='update_user'),
    path('perfil/excluir/', views.delete_user, name='delete_user'),
    path('mapa/', views.pontos_coleta, name='pontos_coleta'),
    path('cadastro/parceiro/', views.partner_register, name='partner_register'),
    path('login/parceiro/', views.login_partner, name='login_partner'), # Nova rota
    path('login/parceiro/', views.login_partner, name='login_partner'), 
    path('parceiro/', views.partner_area, name='partner_area'),
    path('parceiro/atualizar/', views.update_partner, name='update_partner'),
    path('parceiro/pontos/', views.manage_collection_points, name='manage_collection_points'),
    path('parceiro/pontos/criar/', views.create_collection_point, name='create_collection_point'),
]