from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_wtf.csrf import CSRFProtect
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from config_flask import *
import mysql.connector
from werkzeug.security import generate_password_hash
from passlib.hash import pbkdf2_sha256
from forms.formsLogin.forms import LoginForm, RegisterForm
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object('config_flask')
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONFIG['mysql']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

# Configuración de Flask-Login (desactivado por ahora)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login.login'

# Usar la configuración de MySQL
db_config = DATABASE_CONFIG['mysql']

db = SQLAlchemy(app)

# class User:
#     def __init__(self, user_data):
#         self.id = user_data['id']
#         self.email = user_data['email']
#         self.rol = user_data['rol']
#         self.is_active = user_data.get('is_active', True)
#         self.is_authenticated = True
#         self.is_anonymous = False
# 
#     def get_id(self):
#         return str(self.id)

# @login_manager.user_loader
# def load_user(user_id):
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM usuario WHERE id = %s", (user_id,))
#         user_data = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         
#         if user_data:
#             return User(user_data)
#         return None
#     except Exception as e:
#         print(f"Error al cargar usuario: {e}")
#         return None

# Definir la URL base de la API
API_BASE_URL = API_URL

# Importar y registrar blueprints
from views.vistaMain.vistaMain import main_bp
from views.vistaLogin.vistaLogin import login_bp
from views.vistaIdeas.vistaIdeas import ideas_bp
from views.vistaAuthentication.vistaAuthentication import auth_bp
from views.vistaPerfil.vistaPerfil import perfil_bp
from views.vistaOportunidades.vistaOportunidades import oportunidades_bp
from views.vistaSoluciones.vistaSoluciones import soluciones_bp

app.register_blueprint(main_bp)
app.register_blueprint(login_bp)
app.register_blueprint(ideas_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(oportunidades_bp)
app.register_blueprint(soluciones_bp)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
