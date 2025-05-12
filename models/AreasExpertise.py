from . import db

class AreasExpertise(db.Model):
    __tablename__ = 'areas_expertise'
    __table_args__ = {'schema': 'public'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 