from . import db

class Perfil(db.Model):
    __tablename__ = 'perfil'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_email = db.Column(db.String(100), db.ForeignKey('public.usuario.email'), unique=True)
    nombre = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    area_expertise = db.Column(db.String(255))
    info_adicional = db.Column(db.Text) 