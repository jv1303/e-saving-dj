from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.register_user, name='register_user'),
]