from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class PerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es requerido'),
        Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Ingrese un email válido')
    ])
    
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 caracteres')
    ])
    
    cargo = StringField('Cargo', validators=[
        Optional(),
        Length(max=100, message='El cargo no puede tener más de 100 caracteres')
    ])
    
    area = StringField('Área', validators=[
        Optional(),
        Length(max=100, message='El área no puede tener más de 100 caracteres')
    ])
    
    password = PasswordField('Nueva Contraseña', validators=[
        Optional(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    submit = SubmitField('Guardar Cambios') 