from django.shortcuts import render

def home(request):
    return render(request, 'auction/home.html', {})
