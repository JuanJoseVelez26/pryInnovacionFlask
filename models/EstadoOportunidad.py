from . import db

class EstadoOportunidad(db.Model):
    __tablename__ = 'estado_oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 