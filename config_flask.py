import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#1!vjo3l)hf!zh+kzob43t2-f)ssp9z3k-b2@j(@&w9+@6l21@')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Configuración de la base de datos
# Puedes elegir entre SQLite, PostgreSQL o MySQL
DATABASE_CONFIG = {
    # Configuración para SQLite (más simple para desarrollo)
    'sqlite': {
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{BASE_DIR}/db.sqlite3',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    },
    
    # Configuración para PostgreSQL
    'postgresql': {
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:@localhost:5432/bdinnovacion',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    },
    
    # Configuración para MySQL
    'mysql': {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'innovacion_db',
        'SQLALCHEMY_DATABASE_URI': 'mysql://root:@localhost/innovacion_db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
}

# Selecciona la configuración de base de datos a usar
# Cambia 'sqlite' por 'postgresql' o 'mysql' según prefieras
DATABASE_TYPE = 'postgresql'  # Mantenemos PostgreSQL como predeterminado

# Configuración de archivos estáticos y multimedia
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de la API
API_URL = os.environ.get('API_URL', "http://190.217.58.246:5186/api/SGV/procedures/execute")

# Configuración de sesiones
SESSION_TYPE = 'filesystem'  # Opciones: 'filesystem', 'redis', 'memcached', etc.

# Configuración de idioma
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'

# Configuración de autenticación
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/login'

# Configuración de CSRF
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = SECRET_KEY

# Configuración de correo electrónico (si es necesario)
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'user@example.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'password')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

# Configuración de carga de archivos
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max-limit 