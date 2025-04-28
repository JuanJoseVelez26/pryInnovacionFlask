from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# Tabla de asociación para la relación muchos a muchos entre Usuario e Idea
idea_usuario = db.Table('idea_usuario',
    db.Column('usuario_email', db.String(100), db.ForeignKey('usuario.email'), primary_key=True),
    db.Column('idea_id', db.Integer, db.ForeignKey('idea.id'), primary_key=True)
)

# Tabla de asociación para la relación muchos a muchos entre Usuario y Oportunidad
oportunidad_usuario = db.Table('oportunidad_usuario',
    db.Column('usuario_email', db.String(100), db.ForeignKey('usuario.email'), primary_key=True),
    db.Column('oportunidad_id', db.Integer, db.ForeignKey('oportunidad.id'), primary_key=True)
)

# Modelo de Usuario
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    __table_args__ = {'extend_existing': True}

    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    # Agrega aquí los demás campos que tenga tu tabla, por ejemplo:
    # nombre = db.Column(db.String(100), nullable=False)
    # fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    # activo = db.Column(db.Boolean, default=True)

    # Relaciones
    perfil = db.relationship('Perfil', backref='usuario', uselist=False, cascade='all, delete-orphan')
    ideas = db.relationship('Idea', secondary=idea_usuario, backref='usuarios')
    oportunidades = db.relationship('Oportunidad', secondary=oportunidad_usuario, backref='usuarios')

    def get_id(self):
        return self.email

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

# Modelo de Perfil
class Perfil(db.Model):
    __tablename__ = 'perfil'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_email = db.Column(db.String(100), db.ForeignKey('usuario.email'), unique=True)
    telefono = db.Column(db.String(20))
    area_expertise_id = db.Column(db.Integer, db.ForeignKey('areas_expertise.id'))
    descripcion = db.Column(db.Text)
    avatar = db.Column(db.String(255))

# Modelo de Idea
class Idea(db.Model):
    __tablename__ = 'idea'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area_i.id'))
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_i.id'))
    tipo_innovacion_id = db.Column(db.Integer, db.ForeignKey('tipo_innovacion.id'))
    foco_innovacion_id = db.Column(db.Integer, db.ForeignKey('foco_innovacion.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    creador_email = db.Column(db.String(100), db.ForeignKey('usuario.email'))
    
    # Relaciones
    area = db.relationship('AreaI')
    estado = db.relationship('EstadoI')
    tipo_innovacion = db.relationship('TipoInnovacion')
    foco_innovacion = db.relationship('FocoInnovacion')
    creador = db.relationship('Usuario', foreign_keys=[creador_email])

# Modelo de Oportunidad
class Oportunidad(db.Model):
    __tablename__ = 'oportunidad'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area_o.id'))
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_o.id'))
    tipo_oportunidad_id = db.Column(db.Integer, db.ForeignKey('tipo_oportunidad.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    creador_email = db.Column(db.String(100), db.ForeignKey('usuario.email'))
    
    # Relaciones
    area = db.relationship('AreaO')
    estado = db.relationship('EstadoO')
    tipo_oportunidad = db.relationship('TipoOportunidad')
    creador = db.relationship('Usuario', foreign_keys=[creador_email])

# Modelo de Proyecto
class Proyecto(db.Model):
    __tablename__ = 'proyecto'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'))
    oportunidad_id = db.Column(db.Integer, db.ForeignKey('oportunidad.id'))
    estado = db.Column(db.String(50))
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    creador_email = db.Column(db.String(100), db.ForeignKey('usuario.email'))
    
    # Relaciones
    idea = db.relationship('Idea')
    oportunidad = db.relationship('Oportunidad')
    creador = db.relationship('Usuario', foreign_keys=[creador_email])

# Modelo de Solución
class Solucion(db.Model):
    __tablename__ = 'solucion'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'))
    estado = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    creador_email = db.Column(db.String(100), db.ForeignKey('usuario.email'))
    
    # Relaciones
    proyecto = db.relationship('Proyecto')
    creador = db.relationship('Usuario', foreign_keys=[creador_email])

# Modelos de soporte
class AreaI(db.Model):
    __tablename__ = 'area_i'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class EstadoI(db.Model):
    __tablename__ = 'estado_i'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class AreaO(db.Model):
    __tablename__ = 'area_o'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class EstadoO(db.Model):
    __tablename__ = 'estado_o'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class TipoInnovacion(db.Model):
    __tablename__ = 'tipo_innovacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class FocoInnovacion(db.Model):
    __tablename__ = 'foco_innovacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class TipoOportunidad(db.Model):
    __tablename__ = 'tipo_oportunidad'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class AreasExpertise(db.Model):
    __tablename__ = 'areas_expertise'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False) 