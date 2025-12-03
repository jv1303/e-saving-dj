from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('quem_somos/', views.quem_somos, name='quem_somos'),
    path('area_parceiro/', views.area_parceiro, name='area_parceiro'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]