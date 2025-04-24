from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class IdeaForm(FlaskForm):
    titulo = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=5, max=100, message='El título debe tener entre 5 y 100 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida'),
        Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
    ])
    
    palabras_claves = StringField('Palabras Claves', validators=[
        DataRequired(message='Las palabras claves son requeridas'),
        Length(max=200, message='Las palabras claves no pueden exceder los 200 caracteres')
    ])
    
    recursos_requeridos = TextAreaField('Recursos Requeridos', validators=[
        Optional(),
        Length(max=500, message='Los recursos requeridos no pueden exceder los 500 caracteres')
    ])
    
    id_tipo_innovacion = SelectField('Tipo de Innovación', coerce=int, validators=[
        DataRequired(message='El tipo de innovación es requerido')
    ])
    
    id_foco_innovacion = SelectField('Foco de Innovación', coerce=int, validators=[
        DataRequired(message='El foco de innovación es requerido')
    ])
    
    mensaje_experto = TextAreaField('Mensaje para el Experto', validators=[
        Optional(),
        Length(max=500, message='El mensaje no puede exceder los 500 caracteres')
    ])
    
    submit = SubmitField('Guardar Idea') 