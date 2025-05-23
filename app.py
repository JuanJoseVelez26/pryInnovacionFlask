from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import os
from config_flask import FLASK_CONFIG, API_CONFIG
from forms.formsLogin.forms import LoginForm, RegisterForm
from dotenv import load_dotenv
from views.vistaLogin.vistaLogin import login_bp
from views.vistaIdeas.vistaIdeas import ideas_bp
from views.vistaOportunidades.vistaOportunidades import oportunidades_bp
from views.vistaSoluciones.vistaSoluciones import soluciones_bp
from views.vistaPerfil.vistaPerfil import perfil_bp
from views.vistaDashboard.vistaDashboard import dashboard_bp
from views.vistaMain.vistaMain import main_bp
from views.vistaProyectos.vistaProyectos import proyectos_bp
from utils.api_client import APIClient

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración básica
app.config.update(FLASK_CONFIG)

# Configuración de CSRF
csrf = CSRFProtect(app)

# Configuración de la sesión
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Asegura que la sesión esté encriptada
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = False  # Para desarrollo local

# Inicializar el cliente API
api_client = APIClient(API_CONFIG['base_url'])

# Registrar los blueprints
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(ideas_bp)
app.register_blueprint(oportunidades_bp)
app.register_blueprint(soluciones_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(main_bp)
app.register_blueprint(proyectos_bp)

@app.route('/')
def index():
    if not session.get('user_email'):
        return redirect(url_for('login.login_view'))
    return redirect(url_for('dashboard.index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
