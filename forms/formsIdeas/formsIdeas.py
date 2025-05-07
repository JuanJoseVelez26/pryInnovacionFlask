import requests
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField,
    IntegerField, DateField, SelectField
)
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField


def obtener_focos_innovacion():
    """
    Consulta la API de focos de innovación y retorna una lista de tuplas
    (id, nombre) para usar en los SelectField.
    """
    url = "http://190.217.58.246:5186/api/sgv/foco_innovacion"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return [
            (foco['id_foco_innovacion'], foco['name'])
            for foco in resp.json()
        ]
    except requests.RequestException:
        return []


def obtener_tipos_innovacion():
    """
    Consulta la API de tipos de innovación y retorna una lista de tuplas
    (id, nombre) para usar en los SelectField.
    """
    url = "http://190.217.58.246:5186/api/sgv/tipo_innovacion"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return [
            (tipo['id_tipo_innovacion'], tipo['name'])
            for tipo in resp.json()
        ]
    except requests.RequestException:
        return []


class IdeasForm(FlaskForm):
    titulo = StringField(
        'Título',
        validators=[DataRequired(), Length(max=255)],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Ingrese el título de la idea'
        }
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[DataRequired()],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Proporcione una descripción detallada de la idea'
        }
    )
    recursos_requeridos = IntegerField(
        'Recursos Requeridos',
        validators=[DataRequired()],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Cantidad de recursos necesarios'
        }
    )
    palabras_claves = StringField(
        'Palabras Claves',
        validators=[DataRequired(), Length(max=255)],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Palabras clave relacionadas con la idea'
        }
    )
    fecha_creacion = DateField(
        'Fecha de Creación',
        validators=[DataRequired()],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control',
            'type': 'date'
        }
    )
    archivo_multimedia = FileField(
        'Archivos Multimedia',
        validators=[Optional()],
        render_kw={
            'class': 'form-control'
        }
    )

    id_foco_innovacion = SelectField(
        'Foco de Innovación',
        coerce=int,
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    id_tipo_innovacion = SelectField(
        'Tipo de Innovación',
        coerce=int,
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar dinámicamente las opciones al instanciar el formulario
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()


class IdeasUpdateForm(IdeasForm):
    mensaje_experto = TextAreaField(
        'Mensaje del Experto',
        validators=[Optional()],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Deja tu mensaje como experto aquí'
        }
    )
