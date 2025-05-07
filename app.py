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
from models import (
    db, Usuario, Perfil, Idea, Oportunidad, Proyecto, Solucion,
    AreaIdea, EstadoIdea, AreaOportunidad, EstadoOportunidad,
    TipoInnovacion, FocoInnovacion, TipoOportunidad, AreasExpertise,
    Aplicacion, Rol, IdeaUsuario, OportunidadUsuario, Notificaciones
)

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Configuración de la base de datos
app.config.update(DATABASE_CONFIG[DATABASE_TYPE])

# Configuración de CSRF
csrf = CSRFProtect(app)

# Configuración del sistema de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

# Inicializar SQLAlchemy con la aplicación
db.init_app(app)

# Asegurar que todas las tablas existan
def init_db():
    try:
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            
            # Verificar que las tablas principales existan
            inspector = db.inspect(db.engine)
            tablas_requeridas = ['usuario', 'idea', 'oportunidad', 'idea_usuario', 'oportunidad_usuario']
            tablas_existentes = inspector.get_table_names(schema='public')
            
            tablas_faltantes = [tabla for tabla in tablas_requeridas if tabla not in tablas_existentes]
            
            if tablas_faltantes:
                print(f"Advertencia: Las siguientes tablas no se crearon correctamente: {', '.join(tablas_faltantes)}")
            else:
                print("Base de datos inicializada correctamente")
                
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        raise

# Inicializar la base de datos al arrancar la aplicación
init_db()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Importar y registrar blueprints
from views.vistaMain.vistaMain import main_bp
from views.vistaLogin.vistaLogin import login_bp
from views.vistaIdeas.vistaIdeas import ideas_bp
from views.vistaAuthentication.vistaAuthentication import auth_bp
from views.vistaPerfil.vistaPerfil import perfil_bp
from views.vistaOportunidades.vistaOportunidades import oportunidades_bp
from views.vistaSoluciones.vistaSoluciones import soluciones_bp

# Registrar los blueprints
app.register_blueprint(main_bp)
app.register_blueprint(login_bp)
app.register_blueprint(ideas_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(perfil_bp)
app.register_blueprint(oportunidades_bp)
app.register_blueprint(soluciones_bp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Redirigir directamente al dashboard
        return redirect(url_for('auth.dashboard'))
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

@app.route('/test-db')
def test_db():
    try:
        # Intentar hacer una consulta simple
        usuarios = Usuario.query.all()
        return {
            'status': 'success',
            'message': 'Conexión a la base de datos exitosa',
            'usuarios_count': len(usuarios)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error de conexión: {str(e)}'
        }

@app.route('/test-models')
def test_models():
    resultados = {}
    modelos = [
        (Usuario, 'Usuario'),
        (Idea, 'Idea'),
        (Oportunidad, 'Oportunidad'),
        (Proyecto, 'Proyecto'),
        (Solucion, 'Solucion'),
        (AreaIdea, 'AreaIdea'),
        (EstadoIdea, 'EstadoIdea'),
        (AreaOportunidad, 'AreaOportunidad'),
        (EstadoOportunidad, 'EstadoOportunidad'),
        (TipoInnovacion, 'TipoInnovacion'),
        (FocoInnovacion, 'FocoInnovacion'),
        (TipoOportunidad, 'TipoOportunidad'),
        (AreasExpertise, 'AreasExpertise'),
        (Perfil, 'Perfil'),
        (Aplicacion, 'Aplicacion'),
        (Rol, 'Rol'),
        (IdeaUsuario, 'IdeaUsuario'),
        (OportunidadUsuario, 'OportunidadUsuario'),
        (Notificaciones, 'Notificaciones')
    ]
    
    for modelo, nombre in modelos:
        try:
            registros = modelo.query.all()
            resultados[nombre] = {
                'status': 'success',
                'count': len(registros),
                'message': 'Consulta exitosa'
            }
        except Exception as e:
            resultados[nombre] = {
                'status': 'error',
                'message': str(e)
            }
    
    return resultados

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
