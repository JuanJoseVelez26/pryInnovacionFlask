from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login:login')  # Redirige a la página de inicio de sesión o a donde desees