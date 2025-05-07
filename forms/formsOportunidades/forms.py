from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class OportunidadForm(FlaskForm):
    titulo = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=5, max=100, message='El título debe tener entre 5 y 100 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida'),
        Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
    ])
    
    palabras_claves = StringField('Palabras Clave', validators=[
        DataRequired(message='Las palabras clave son requeridas'),
        Length(min=3, max=200, message='Las palabras clave deben tener entre 3 y 200 caracteres')
    ])
    
    recursos_requeridos = TextAreaField('Recursos Requeridos', validators=[
        DataRequired(message='Los recursos requeridos son necesarios'),
        Length(min=10, max=500, message='Los recursos requeridos deben tener entre 10 y 500 caracteres')
    ])
    
    id_tipo_innovacion = SelectField('Tipo de Innovación', coerce=int, validators=[
        DataRequired(message='El tipo de innovación es requerido')
    ])
    
    id_foco_innovacion = SelectField('Foco de Innovación', coerce=int, validators=[
        DataRequired(message='El foco de innovación es requerido')
    ])
    
    submit = SubmitField('Guardar') 
    
class OportunidadUpdateForm(FlaskForm):
    titulo = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=5, max=100, message='El título debe tener entre 5 y 100 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida'),
        Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
    ])
    
    palabras_claves = StringField('Palabras Clave', validators=[
        Length(min=3, max=200, message='Las palabras clave deben tener entre 3 y 200 caracteres')
    ])
    
    recursos_requeridos = TextAreaField('Recursos Requeridos', validators=[
        Length(min=10, max=500, message='Los recursos requeridos deben tener entre 10 y 500 caracteres')
    ])
    
    id_tipo_innovacion = SelectField('Tipo de Innovación', coerce=int, validators=[
        DataRequired(message='El tipo de innovación es requerido')
    ])
    
    id_foco_innovacion = SelectField('Foco de Innovación', coerce=int, validators=[
        DataRequired(message='El foco de innovación es requerido')
    ])
    
    submit = SubmitField('Actualizar')