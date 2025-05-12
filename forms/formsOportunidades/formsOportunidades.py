from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class OportunidadForm(FlaskForm):
    titulo = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida'),
        Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
    ])
    
    palabras_claves = StringField('Palabras Clave', validators=[
        DataRequired(message='Las palabras clave son requeridas'),
        Length(max=200, message='Las palabras clave no deben exceder los 200 caracteres')
    ])
    
    recursos_requeridos = TextAreaField('Recursos Requeridos', validators=[
        DataRequired(message='Los recursos requeridos son necesarios'),
        Length(max=500, message='Los recursos requeridos no deben exceder los 500 caracteres')
    ])
    
    tipo_mercado = SelectField('Tipo de Mercado', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un tipo de mercado')
    ])
    
    estado = SelectField('Estado', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un estado')
    ])
    
    submit = SubmitField('Guardar')
