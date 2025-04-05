from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, FileField, SelectField
from wtforms.validators import DataRequired, Length
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
        validators=[DataRequired(), Length(max=255)],
        render_kw={"class": "form-control", "placeholder": "Ingrese el título de la idea"}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[DataRequired()],
        render_kw={"class": "form-control", "placeholder": "Proporcione una descripción detallada de la idea"}
    )
    
    recursos_requeridos = IntegerField(
        'Recursos Requeridos',
        validators=[DataRequired()],
        render_kw={"class": "form-control", "placeholder": "Cantidad de recursos necesarios"}
    )
    
    palabras_claves = StringField(
        'Palabras Claves',
        validators=[DataRequired(), Length(max=255)],
        render_kw={"class": "form-control", "placeholder": "Palabras clave relacionadas con la idea"}
    )
    
    fecha_creacion = DateField(
        'Fecha de Creación',
        validators=[DataRequired()],
        format='%Y-%m-%d',
        render_kw={"class": "form-control", "type": "date"}
    )
    
    archivo_multimedia = FileField(
        'Archivos Multimedia',
        render_kw={"class": "form-control"}
    )
    
    id_foco_innovacion = SelectField(
        'Foco de Innovación',
        choices=[],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    
    id_tipo_innovacion = SelectField(
        'Tipo de Innovación',
        choices=[],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con datos dinámicos de la API"""
        super(IdeasForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()