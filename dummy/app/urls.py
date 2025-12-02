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
]