from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()

# Importar modelos SQLAlchemy
from .Usuario import Usuario
from .Idea import Idea
from .Oportunidad import Oportunidad
from .Solucion import Solucion
from .TipoInnovacion import TipoInnovacion
from .FocoInnovacion import FocoInnovacion
from .Perfil import Perfil

# Configurar el login manager
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

# Exportar todos los modelos
__all__ = [
    'db',
    'login_manager',
    'Usuario',
    'Idea',
    'Oportunidad',
    'Solucion',
    'TipoInnovacion',
    'FocoInnovacion',
    'Perfil'
]
