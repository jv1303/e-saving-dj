from django.shortcuts import render, HttpResponse

def home(response):
    return render(response, 'home.html', {"logged": False})