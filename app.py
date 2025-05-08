from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from config_flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256
from forms.formsLogin.forms import LoginForm, RegisterForm
from dotenv import load_dotenv
from models import db, Usuario, Perfil, Idea, Oportunidad, Proyecto, Solucion

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object('config_flask')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONFIG[DATABASE_TYPE]['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

# Usar la configuración de MySQL
db_config = DATABASE_CONFIG['mysql']

# Inicializar SQLAlchemy
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Redirigir directamente al dashboard
        return redirect(url_for('dashboard'))
    return render_template('templatesLogin/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login.login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        new_user = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            password=hashed_password
        )
        
        db.session.add(new_user)
        
        # Crear perfil asociado
        new_profile = Perfil(
            usuario=new_user,
            descripcion=form.descripcion.data,
            area_expertise_id=form.area_expertise.data
        )
        db.session.add(new_profile)
        
        try:
            db.session.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar usuario. Por favor intenta nuevamente.', 'error')
    
    return render_template('templatesLogin/register.html', form=form)

@app.route('/dashboard')
def dashboard():
    # Crear un usuario temporal para la sesión
    session['user_email'] = 'usuario@temporal.com'
    session['user_name'] = 'Usuario Temporal'
    session['user_role'] = 'Usuario'
    
    # Datos temporales para el dashboard
    dashboard_data = {
        'total_ideas': 0,
        'total_opportunities': 0,
        'total_projects': 0,
        'recent_activities': []
    }
    
    return render_template('dashboard.html', **dashboard_data)

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
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
