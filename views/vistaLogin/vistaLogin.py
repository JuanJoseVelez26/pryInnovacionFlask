from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from forms.formsLogin.forms import LoginForm, RegisterForm
from utils.api_client import APIClient
from flask_login import login_user, logout_user, current_user, UserMixin
from config_flask import API_CONFIG

login_bp = Blueprint('login', __name__)
api_client = APIClient(API_CONFIG['base_url'])

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['email']
        self.email = user_data['email']
        self.is_active = user_data.get('is_active', True)
        self.is_staff = user_data.get('is_staff', False)

@login_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    # Verificar si ya hay sesión activa
    if session.get('user_email'):
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            # Intentar login a través del API
            print(f'Intentando autenticar usuario: {email}')
            response = api_client.login(email, password)
            
            if not response:
                flash('Correo electrónico o contraseña inválidos.', 'danger')
                return render_template('templatesLogin/login.html', form=form)

            # La respuesta del API de C# puede venir en una estructura diferente
            # Vamos a imprimir la respuesta completa para ver su estructura
            print(f'Respuesta completa del API: {response}')
            
            # Almacenar datos en la sesión
            print('Guardando datos en la sesión...')
            session['user_email'] = email  # Guardar el email usado para el login
            session['user_name'] = email.split('@')[0]  # Usar la parte local del email como nombre de usuario
            print(f'Datos guardados en sesión: {dict(session)}')
            
            # Establecer la sesión como permanente
            session.permanent = True
            
            flash('Inicio de sesión exitoso', 'success')
            # Redirigir al dashboard
            return redirect(url_for('dashboard.index'))

        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')
            print(f'Error de login: {str(e)}')

    return render_template('templatesLogin/login.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    form = RegisterForm()
    if form.validate_on_submit():
        user_data = {
            'nombre': form.nombre.data,
            'apellido': form.apellido.data,
            'email': form.email.data,
            'password': form.password.data,
            'perfil': form.perfil.data
        }
        
        response = api_client.register(user_data)
        if response:
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login.login_view'))
        else:
            flash('Error al registrar usuario. Por favor intenta nuevamente.', 'error')
    
    return render_template('templatesLogin/register.html', form=form)

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login.login_view'))
