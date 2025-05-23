from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email
import requests

# Funciones para obtener datos desde la API
def obtener_focos_innovacion():
    response = requests.get("http://localhost:5186/api/InnovacionUSB/FocoInnovacion")
    if response.status_code == 200:
        return [(foco['id_foco_innovacion'], foco['name']) for foco in response.json()]
    return [(1, 'Foco 1'), (2, 'Foco 2')]  # Valores por defecto

def obtener_tipos_innovacion():
    response = requests.get("http://localhost:5186/api/InnovacionUSB/TipoInnovacion")
    if response.status_code == 200:
        return [(tipo['id_tipo_innovacion'], tipo['name']) for tipo in response.json()]
    return [(1, 'Tipo 1'), (2, 'Tipo 2')]  # Valores por defecto

class IdeasForm(FlaskForm):
    titulo = StringField(
        'Título',
        validators=[
            DataRequired(message='El título es requerido'),
            Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Ingrese el título de la idea"}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Proporcione una descripción detallada de la idea"}
    )
    
    palabras_claves = StringField(
        'Palabras Claves',
        validators=[
            DataRequired(message='Las palabras claves son requeridas'),
            Length(max=200, message='Las palabras claves no pueden exceder los 200 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Palabras clave relacionadas con la idea"}
    )
    
    recursos_requeridos = TextAreaField(
        'Recursos Requeridos',
        validators=[
            DataRequired(message='Los recursos requeridos son necesarios'),
            Length(max=500, message='Los recursos requeridos no deben exceder los 500 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Describa los recursos necesarios"}
    )
    
    foco_innovacion = SelectField(
        'Foco de Innovación',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un foco de innovación')],
        render_kw={"class": "form-control"}
    )
    
    tipo_innovacion = SelectField(
        'Tipo de Innovación',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un tipo de innovación')],
        render_kw={"class": "form-control"}
    )
    
    mensaje_experto = TextAreaField(
        'Mensaje del Experto',
        validators=[
            Optional(),
            Length(max=500, message='El mensaje no puede exceder los 500 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Mensaje del experto sobre la idea"}
    )
    
    archivo_multimedia = FileField(
        'Archivos Multimedia',
        render_kw={"class": "form-control"}
    )
    
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con datos dinámicos de la API"""
        super(IdeasForm, self).__init__(*args, **kwargs)
        self.foco_innovacion.choices = obtener_focos_innovacion()
        self.tipo_innovacion.choices = obtener_tipos_innovacion()