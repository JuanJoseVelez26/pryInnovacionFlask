from . import db

class EtapaOportunidad(db.Model):
    __tablename__ = 'etapa_oportunidad'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 