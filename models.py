from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

# Crear instancia de SQLAlchemy
db = SQLAlchemy()

# Modelo de Usuario
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'public'}

    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

    def get_id(self):
        return self.email

    def is_active(self):
        return self.estado

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

# Modelo de Perfil
class Perfil(db.Model):
    __tablename__ = 'login_perfil'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_email = db.Column(db.String(100))
    rol_id = db.Column(db.Integer)
    aplicacion_id = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Modelo de Aplicación
class Aplicacion(db.Model):
    __tablename__ = 'aplicacion'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Modelo de Rol
class Rol(db.Model):
    __tablename__ = 'rol'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Modelo de Idea
class Idea(db.Model):
    __tablename__ = 'idea'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    area_id = db.Column(db.Integer)
    estado_id = db.Column(db.Integer)
    tipo_innovacion_id = db.Column(db.Integer)
    foco_innovacion_id = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Modelo de Oportunidad
class Oportunidad(db.Model):
    __tablename__ = 'oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    area_id = db.Column(db.Integer)
    estado_id = db.Column(db.Integer)
    tipo_oportunidad_id = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Modelo de Proyecto
class Proyecto(db.Model):
    __tablename__ = 'proyecto'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    idea_id = db.Column(db.Integer)
    oportunidad_id = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.String(50))

# Modelo de Solución
class Solucion(db.Model):
    __tablename__ = 'solucion'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    proyecto_id = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.String(50))

# Modelos de catálogos
class AreaIdea(db.Model):
    __tablename__ = 'area_idea'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class EstadoIdea(db.Model):
    __tablename__ = 'estado_idea'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class AreaOportunidad(db.Model):
    __tablename__ = 'area_oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class EstadoOportunidad(db.Model):
    __tablename__ = 'estado_oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class TipoInnovacion(db.Model):
    __tablename__ = 'tipo_innovacion'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class FocoInnovacion(db.Model):
    __tablename__ = 'foco_innovacion'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class TipoOportunidad(db.Model):
    __tablename__ = 'tipo_oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class AreasExpertise(db.Model):
    __tablename__ = 'areas_expertise'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

# Tablas de asociación
class IdeaUsuario(db.Model):
    __tablename__ = 'idea_usuario'
    __table_args__ = {'schema': 'public'}
    
    usuario_email = db.Column(db.String(100), primary_key=True)
    idea_id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class OportunidadUsuario(db.Model):
    __tablename__ = 'oportunidad_usuario'
    __table_args__ = {'schema': 'public'}
    
    usuario_email = db.Column(db.String(100), primary_key=True)
    oportunidad_id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_email = db.Column(db.String(100))
    titulo = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)
    usuario_creacion = db.Column(db.String(100))
    usuario_modificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True) 