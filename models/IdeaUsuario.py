from . import db

class IdeaUsuario(db.Model):
    __tablename__ = 'idea_usuario'
    __table_args__ = {'schema': 'public'}
    
    codigo_idea = db.Column(db.Integer, db.ForeignKey('public.idea.codigo_idea'), primary_key=True)
    usuario_email = db.Column(db.String(100), db.ForeignKey('public.usuario.email'), primary_key=True) 