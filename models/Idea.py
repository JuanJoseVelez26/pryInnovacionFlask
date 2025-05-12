from . import db

class Idea(db.Model):
    __tablename__ = 'idea'
    __table_args__ = {'schema': 'public'}
    
    codigo_idea = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    palabras_claves = db.Column(db.String(255))
    recursos_requeridos = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime)
    estado = db.Column(db.Boolean, default=False)
    usuario_email = db.Column(db.String(100), db.ForeignKey('public.usuario.email'))
    id_tipo_innovacion = db.Column(db.Integer, db.ForeignKey('public.tipo_innovacion.id_tipo_innovacion'))
    id_foco_innovacion = db.Column(db.Integer, db.ForeignKey('public.foco_innovacion.id_foco_innovacion'))
    id_area = db.Column(db.Integer, db.ForeignKey('public.area_idea.id_area'))
    id_estado = db.Column(db.Integer, db.ForeignKey('public.estado_idea.id_estado')) 