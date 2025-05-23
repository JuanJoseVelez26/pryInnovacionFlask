from . import db

class FocoInnovacion(db.Model):
    __tablename__ = 'foco_innovacion'
    __table_args__ = {'schema': 'public'}
    
    id_foco_innovacion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 