from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import login
from ..forms.registro_form import RegisterForm
from ..models import APIClient
from django.contrib.auth.hashers import make_password

# En la vista de registro (registro_usuario)
def registro_usuario(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Extraer datos del formulario
            email = form.cleaned_data['email']
            contrasena = form.cleaned_data['password1']
            nombre = form.cleaned_data['nombre']
            rol = 'Usuario'  # Rol por defecto
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            direccion = form.cleaned_data['direccion']
            descripcion = form.cleaned_data['descripcion']
            area_expertise = form.cleaned_data['area_expertise']
            informacion_adicional = form.cleaned_data['informacion_adicional']
            
            # Encriptar contraseña
            contrasena_encriptada = make_password(contrasena)

            # Datos del usuario
            usuario_data = {
                "email": email,
                "password": contrasena_encriptada,
                "is_active": False,
                "is_staff": False,
                "is_superuser": False,
                "last_login": None
            }

            # Crear usuario
            usuario_client = APIClient('usuario')
            usuario_response = usuario_client.insert_data(json_data=usuario_data)
            
            if usuario_response and 'outputParams' in usuario_response:
                # Datos del perfil
                perfil_data = {
                    "usuario_email": email,
                    "nombre": nombre,
                    "rol": rol,
                    "fecha_nacimiento": str(fecha_nacimiento),
                    "direccion": direccion,
                    "descripcion": descripcion
                }

                perfil_client = APIClient('perfil')
                perfil_response = perfil_client.insert_data(json_data=perfil_data)

                if perfil_response and 'outputParams' in perfil_response:
                    # Registro de áreas de expertise
                    if area_expertise:
                        area_client = APIClient('areas_expertise')
                        area_data = {
                            "usuario_email": email,
                            "area": area_expertise
                        }
                        area_response = area_client.insert_data(json_data=area_data)
                    
                    # Registro de información adicional
                    if informacion_adicional:
                        info_client = APIClient('informacion_adicional')
                        info_data = {
                            "usuario_email": email,
                            "info": informacion_adicional
                        }
                        info_response = info_client.insert_data(json_data=info_data)
                    
                    # Redirigir al inicio de sesión si todo fue exitoso
                    return redirect('login:login')
                else:
                    return render(request, 'login/register.html', {'form': form, 'error': 'Error al crear el perfil.'})
            else:
                return render(request, 'login/register.html', {'form': form, 'error': 'Error al crear el usuario.'})
        else:
            return render(request, 'login/register.html', {'form': form, 'error': 'Formulario inválido.'})
    else:
        form = RegisterForm()
        return render(request, 'login/register.html', {'form': form})