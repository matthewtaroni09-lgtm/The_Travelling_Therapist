from django.shortcuts import render

def home(request):
    return render(request, 'auction/index.html', {})

def login(request):
    return render(request, 'auction/login.html', {})
