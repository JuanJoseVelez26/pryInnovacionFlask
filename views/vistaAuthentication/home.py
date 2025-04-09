# authentication/views/home.py
from django.shortcuts import render


def home(request):
    print("Home vista llamada")
    return render(request, 'home.html')
    
#def app(request):
    #return render(request, 'app.html')