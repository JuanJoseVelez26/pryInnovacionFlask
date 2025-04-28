from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    area_expertise = StringField('Área de Expertise')
    informacion_adicional = TextAreaField('Información Adicional')
    submit = SubmitField('Registrarse') 