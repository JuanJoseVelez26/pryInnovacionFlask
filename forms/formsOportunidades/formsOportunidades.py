from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, FileField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileAllowed
import requests
from datetime import date

# Funciones para cargar datos de la API
def obtener_focos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion")
        data = response.json()
        if isinstance(data, list):
            return [(str(f['id_foco_innovacion']), f['name']) for f in data]
    except Exception as e:
        print(f"Error al obtener focos: {e}")
    return []

def obtener_tipos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion")
        data = response.json()
        if isinstance(data, list):
            return [(str(t['id_tipo_innovacion']), t['name']) for t in data]
    except Exception as e:
        print(f"Error al obtener tipos: {e}")
    return []

# Validación personalizada de la fecha para asegurarse que no sea futura
def validar_fecha_no_futura(form, field):
    if field.data > date.today():
        raise ValidationError("La fecha no puede ser futura.")

# Formulario Flask
class OportunidadesUpdateForm(FlaskForm):
    titulo = StringField(
        'Título',
        validators=[DataRequired(), Length(max=255)],
        render_kw={"class": "form-control", "placeholder": "Ingrese el título de la oportunidad"}
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[DataRequired()],
        render_kw={"class": "form-control", "placeholder": "Proporcione una descripción detallada"}
    )

    recursos_requeridos = IntegerField(
        'Recursos Requeridos',
        validators=[DataRequired()],
        render_kw={"class": "form-control", "placeholder": "Cantidad de recursos necesarios"}
    )

    palabras_claves = StringField(
        'Palabras Claves',
        validators=[DataRequired(), Length(max=255)],
        render_kw={"class": "form-control", "placeholder": "Palabras clave relacionadas con la oportunidad"}
    )

    fecha_creacion = DateField(
        'Fecha de Creación',
        validators=[DataRequired(), validar_fecha_no_futura],
        render_kw={"class": "form-control", "type": "date"}
    )

    archivo_multimedia = FileField(
        'Archivos Multimedia',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'mp4', 'pdf'], 'Formato de archivo no válido')],
        render_kw={"class": "form-control"}
    )

    id_foco_innovacion = SelectField(
        'Foco de Innovación',
        choices=[],  # Se llenan al inicializar
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )

    id_tipo_innovacion = SelectField(
        'Tipo de Innovación',
        choices=[],  # Se llenan al inicializar
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )

    mensaje_experto = TextAreaField(
        'Mensaje del Experto',
        render_kw={"class": "form-control", "placeholder": "Deja tu mensaje como experto aquí"}
    )

    def __init__(self, *args, **kwargs):
        super(OportunidadesUpdateForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()
