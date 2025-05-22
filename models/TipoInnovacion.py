from . import db

class TipoInnovacion(db.Model):
    __tablename__ = 'tipo_innovacion'
    __table_args__ = {'schema': 'public'}
    
    id_tipo_innovacion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 