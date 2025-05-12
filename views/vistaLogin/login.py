from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from utils.api_client import APIClient
from config_flask import API_CONFIG

login_bp = Blueprint('login', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@login_bp.route('/', methods=['GET', 'POST'])
def login_view():
    # Si es GET, mostrar el formulario de login
    if request.method == 'GET':
        return render_template('login/login.html')
        
    # Si el usuario ya está autenticado, redirigir al dashboard
    if 'user_email' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Intentar autenticar con el API
            print(f'Intentando autenticar usuario: {email}')
            response = api_client.login(email, password)
            
            if not response:
                flash('Correo electrónico o contraseña inválidos.', 'danger')
                return render_template('login/login.html')

            # Almacenar datos en la sesión
            print('Guardando datos en la sesión...')
            try:
                # Intentar obtener datos del usuario desde el API
                user_data = api_client.get_user_info(email)
                if user_data:
                    session['user_email'] = email
                    session['user_name'] = email.split('@')[0]
                    session.permanent = True
                    session.modified = True
                else:
                                # Si no hay datos del usuario, usar valores por defecto
                    session['user_email'] = email
                    session['user_name'] = email.split('@')[0]
                    session.permanent = True
                    session.modified = True
            except Exception as e:
                print(f'Error al obtener datos del usuario: {str(e)}')
                # En caso de error, usar valores por defecto
                session['user_email'] = email
                session['user_name'] = email.split('@')[0]
                session['user_role'] = 'Usuario'
                session.permanent = True
                session.modified = True
            print(f'Datos guardados en sesión: {dict(session)}')
            
            flash('Inicio de sesión exitoso', 'success')
            # Redirigir al dashboard
            return redirect(url_for('dashboard.index'))

        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')

    return render_template('login/login.html')
