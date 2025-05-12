from . import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'public'}
    
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    ideas = db.relationship('Idea', backref='usuario', lazy=True, foreign_keys='Idea.usuario_email')
    perfil = db.relationship('Perfil', backref='usuario', uselist=False)
    
    def get_id(self):
        return str(self.email)