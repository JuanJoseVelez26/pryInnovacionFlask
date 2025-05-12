from . import db

class OportunidadUsuario(db.Model):
    __tablename__ = 'oportunidad_usuario'
    __table_args__ = {'schema': 'public'}
    
    oportunidad_id = db.Column(db.Integer, db.ForeignKey('public.oportunidad.id'), primary_key=True)
    usuario_id = db.Column(db.String(100), db.ForeignKey('public.usuario.email'), primary_key=True) 