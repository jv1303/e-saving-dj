from django.shortcuts import render, HttpResponse

def home(response):
    return render(response, 'home.html', {"logged": False})

def about(response):
    return render(response, 'about.html', {"logged": False})

def start(response):
    return render(response, 'start.html', {"logged": False})

def contact(response):
    return render(response, 'contact.html', {"logged": False})