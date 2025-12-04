from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('quem-somos/', views.quem_somos, name='quem_somos'),
    path('mapa/', views.mapa_pontos, name='mapa'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Cadastros
    path('cadastro/cliente/', views.register_cliente, name='register_cliente'),
    path('cadastro/parceiro/', views.register_parceiro, name='register_parceiro'),

    # Área Restrita
    path('minha-area/', views.dashboard, name='dashboard'),
    path('parceiro/novo-ponto/', views.cadastrar_ponto, name='cadastrar_ponto'),
    
    # Itens (Novos)
    path('parceiro/novo-item/', views.adicionar_item, name='adicionar_item'),
    path('parceiro/remover-item/<int:item_id>/', views.remover_item, name='remover_item'),
]
