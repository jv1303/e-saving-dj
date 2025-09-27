from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="Home Page"),
    path("about", views.about, name="About"),
    path("start", views.start, name="Start"),
    path("contact", views.contact, name="Contact")
]