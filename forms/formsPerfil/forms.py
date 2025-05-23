from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class PerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
    ])
    
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[
        Optional()
    ])
    
    direccion = StringField('Dirección', validators=[
        Optional(),
        Length(max=200, message='La dirección no puede exceder los 200 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        Optional(),
        Length(max=500, message='La descripción no puede exceder los 500 caracteres')
    ])
    
    area_expertise = StringField('Área de Expertise', validators=[
        Optional(),
        Length(max=100, message='El área de expertise no puede exceder los 100 caracteres')
    ])
    
    info_adicional = TextAreaField('Información Adicional', validators=[
        Optional(),
        Length(max=500, message='La información adicional no puede exceder los 500 caracteres')
    ])
    
    submit = SubmitField('Guardar Cambios') 