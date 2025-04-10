from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from datetime import datetime
import requests
from config_flask import API_URL
from werkzeug.security import check_password_hash
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Por favor ingrese un email válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        try:
            # Realizamos una llamada al servidor para obtener la información del usuario
            api_url = f"{API_URL}"
            logger.info(f"Intentando conectar a la API: {api_url}")
            
            payload = {
                "procedure": "select_json_entity",
                "parameters": {
                    "table_name": "usuario",
                    "select_columns": "email, password, is_active, is_staff, last_login",
                    "where_condition": f"email = '{self.email.data}'"
                }
            }
            logger.info(f"Payload enviado: {payload}")

            # Realiza la petición para obtener los datos del usuario
            try:
                response = requests.post(api_url, json=payload, timeout=10)
                logger.info(f"Respuesta de la API: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Datos recibidos: {data}")
                    
                    user_data = data.get('outputParams', {}).get('result', [])
                    user_data = user_data[0] if user_data else None

                    if user_data:
                        stored_password = user_data.get('password', '')

                        # Verificación de la contraseña
                        if check_password_hash(stored_password, self.password.data):
                            # Actualizar last_login en la API
                            last_login_str = datetime.now().isoformat()
                            update_payload = {
                                "procedure": "update_json_entity",
                                "parameters": {
                                    "table_name": "usuario",
                                    "set_columns": f"last_login = '{last_login_str}'",
                                    "where_condition": f"email = '{self.email.data}'"
                                }
                            }

                            api_update_url = f"{API_URL}"
                            logger.info(f"Actualizando last_login: {api_update_url}")
                            
                            try:
                                api_update_response = requests.post(api_update_url, json=update_payload, timeout=10)
                                logger.info(f"Respuesta de actualización: {api_update_response.status_code}")
                                
                                if api_update_response.status_code != 200:
                                    logger.error(f"Error al actualizar last_login: {api_update_response.text}")
                                    # Continuamos aunque falle la actualización de last_login
                                    pass
                            except requests.RequestException as e:
                                logger.error(f"Error en la actualización de last_login: {str(e)}")
                                # Continuamos aunque falle la actualización de last_login
                                pass

                            return True
                        else:
                            logger.warning("Contraseña incorrecta")
                            self.password.errors.append("Contraseña incorrecta")
                            return False
                    else:
                        logger.warning("Usuario no encontrado")
                        self.email.errors.append("Usuario no encontrado")
                        return False
                else:
                    logger.error(f"Error en la respuesta de la API: {response.text}")
                    self.email.errors.append(f"Error al conectar con el servicio de autenticación: {response.status_code}")
                    return False
            except requests.Timeout:
                logger.error("Timeout al conectar con la API")
                self.email.errors.append("Tiempo de espera agotado al conectar con el servicio")
                return False
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            self.email.errors.append(f"Error de conexión: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            self.email.errors.append(f"Error inesperado: {str(e)}")
            return False

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Por favor ingrese un email válido')
    ])
    password1 = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debe confirmar la contraseña'),
        EqualTo('password1', message='Las contraseñas no coinciden')
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(max=100, message='El nombre no puede tener más de 100 caracteres')
    ])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es requerida')
    ])
    direccion = StringField('Dirección', validators=[
        DataRequired(message='La dirección es requerida'),
        Length(max=255, message='La dirección no puede tener más de 255 caracteres')
    ])
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida')
    ])
    area_expertise = StringField('Área de expertise', validators=[
        Optional(),
        Length(max=100, message='El área de expertise no puede tener más de 100 caracteres')
    ])
    informacion_adicional = TextAreaField('Información adicional', validators=[
        Optional()
    ]) 