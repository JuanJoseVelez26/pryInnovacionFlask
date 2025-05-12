from . import db

class EstadoIdea(db.Model):
    __tablename__ = 'estado_idea'
    __table_args__ = {'schema': 'public'}
    
    id_estado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 