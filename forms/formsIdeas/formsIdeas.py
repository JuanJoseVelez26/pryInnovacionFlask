from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Optional
import requests

# Funciones para obtener datos desde la API
def obtener_focos_innovacion():
    response = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion")
    if response.status_code == 200:
        return [(str(foco['id_foco_innovacion']), foco['name']) for foco in response.json()]
    return []

def obtener_tipos_innovacion():
    response = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion")
    if response.status_code == 200:
        return [(str(tipo['id_tipo_innovacion']), tipo['name']) for tipo in response.json()]
    return []

class IdeasForm(FlaskForm):
    titulo = StringField(
        'Título',
        validators=[
            DataRequired(message='El título es requerido'),
            Length(min=5, max=100, message='El título debe tener entre 5 y 100 caracteres')
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
            Optional(),
            Length(max=500, message='Los recursos requeridos no pueden exceder los 500 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Describa los recursos necesarios"}
    )
    
    id_foco_innovacion = SelectField(
        'Foco de Innovación',
        coerce=int,
        validators=[DataRequired(message='El foco de innovación es requerido')],
        render_kw={"class": "form-control"}
    )
    
    id_tipo_innovacion = SelectField(
        'Tipo de Innovación',
        coerce=int,
        validators=[DataRequired(message='El tipo de innovación es requerido')],
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

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con datos dinámicos de la API"""
        super(IdeasForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()