from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
from django.db import connection
# from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from ..models import *
from ..exceptions import AuthenticationError, APIConnectionError, UserNotFoundError

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Autenticar usuario a través de la API
            user = Usuario.authenticate(email, password)
            if not user:
                raise AuthenticationError("Correo electrónico o contraseña inválidos.")

            # Obtener los datos de perfil del usuario
            profile = Usuario.get_profile_data(email)
            if not profile:
                raise AuthenticationError("No se encontraron datos de perfil para el usuario.")

            # Verificar si cada campo está presente en el perfil
            if 'fecha_nacimiento' not in profile:
                pass
            if 'info_adicional' not in profile:
                pass
            if 'area_expertise' not in profile:
                pass

            # Convertir fecha de nacimiento a formato datetime si está presente
            fecha_nacimiento = profile.get('fecha_nacimiento', '')
            if fecha_nacimiento:
                try:
                    # Si 'fecha_nacimiento' es una cadena, la convertimos a un objeto datetime
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
                    # Convertir a cadena en formato deseado para almacenar en sesión
                    fecha_nacimiento = fecha_nacimiento.strftime("%d/%m/%Y")
                except ValueError:
                    # Si no se puede convertir, asignamos un valor por defecto
                    fecha_nacimiento = None
            else:
                fecha_nacimiento = None

            # Almacenar los datos del usuario en la sesión, incluyendo los nuevos campos
            request.session['user_email'] = user['email']
            request.session['user_name'] = profile.get('nombre', '')
            request.session['user_role'] = profile.get('rol', '')
            request.session['user_birthdate'] = fecha_nacimiento  # Guardar la fecha de nacimiento como cadena
            request.session['user_address'] = profile.get('direccion', '')
            request.session['user_description'] = profile.get('descripcion', '')
            request.session['user_area_expertise'] = profile.get('area_expertise', '')  # Nuevo campo
            request.session['user_info_adicional'] = profile.get('info_adicional', '')  # Nuevo campo

            # Redirigir a la página principal
            return redirect('authentication:app')

        except AuthenticationError as e:
            return render(request, 'login/login.html', {'error_message': str(e)})

    return render(request, 'login/login.html')
