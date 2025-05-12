from . import db

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.String(100), db.ForeignKey('public.usuario.email'))
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=db.func.now())
    leida = db.Column(db.Boolean, default=False) 