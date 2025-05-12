from . import db

class Aplicacion(db.Model):
    __tablename__ = 'aplicacion'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 