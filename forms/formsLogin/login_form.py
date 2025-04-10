from django import forms
import requests
from django.conf import settings
from login.models import Usuario  # O el modelo que estés usando
from django.contrib.auth.hashers import check_password
from django.utils import timezone

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Realizamos una llamada al servidor para obtener la información del usuario
            api_url = f"{settings.API_URL}usuario"
            payload = {
                "procedure": "select_json_entity",
                "parameters": {
                    "table_name": "usuario",
                    "select_columns": "email, password, is_active, is_staff, last_login",
                    "where_condition": f"email = '{email}'"
                }
            }

            try:
                # Realiza la petición para obtener los datos del usuario
                response = requests.post(api_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    user_data = data['outputParams']['result'][0] if data['outputParams']['result'] else None

                    if user_data:
                        stored_password = user_data['password']  # Contraseña encriptada que viene de la base de datos

                        # Verificación de la contraseña usando check_password
                        if check_password(password, stored_password):
                            # Si la contraseña es correcta, procedemos a continuar con el login

                            # Obtener o crear el usuario en la base de datos
                            user, created = Usuario.objects.get_or_create(
                                email=user_data['email'],
                                defaults={'is_active': user_data['is_active'], 'is_staff': user_data['is_staff']}
                            )

                            # Actualizar manualmente el campo 'last_login' con la fecha y hora actual
                            user.last_login = timezone.now()
                            user.save()  # Guardamos los cambios

                            # Formatear la fecha para la API en formato ISO 8601
                            last_login_str = user.last_login.isoformat()

                            # Crear el payload para actualizar 'last_login' en la base de datos de la API
                            update_payload = {
                                "procedure": "update_json_entity",
                                "parameters": {
                                    "table_name": "usuario",
                                    "set_columns": f"last_login = '{last_login_str}'",
                                    "where_condition": f"email = '{email}'"
                                }
                            }

                            # Realizar la petición para actualizar 'last_login' en la base de datos de la API
                            api_update_url = f"{settings.API_URL}update_usuario"  # Asegúrate de que esta URL sea correcta
                            api_update_response = requests.post(api_update_url, json=update_payload)

                            if api_update_response.status_code == 200:
                                pass  # Fecha de último inicio de sesión actualizada en la API
                            else:
                                raise forms.ValidationError(f"Error al actualizar 'last_login' en la API: {api_update_response.status_code}")

                            cleaned_data['user'] = user  # Se agrega el usuario a cleaned_data
                        else:
                            raise forms.ValidationError("Contraseña incorrecta.")
                    else:
                        raise forms.ValidationError("Usuario no encontrado.")
                else:
                    raise forms.ValidationError("Error al conectar con el servicio de autenticación.")
            except requests.RequestException as e:
                raise forms.ValidationError(f"Error de conexión con el servicio de autenticación: {e}")

        return cleaned_data
