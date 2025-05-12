from . import db

class AreaIdea(db.Model):
    __tablename__ = 'area_idea'
    __table_args__ = {'schema': 'public'}
    
    id_area = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False) 