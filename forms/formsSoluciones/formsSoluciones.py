from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileAllowed
import requests

# Archivos multimedia permitidos
ALLOWED_FILES = ['jpg', 'jpeg', 'png', 'pdf', 'mp4', 'avi']

# Funciones para obtener datos de la API
def obtener_focos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion", timeout=10)
        return [(str(f['id_foco_innovacion']), f['name']) for f in response.json()]
    except Exception:
        return []

def obtener_tipos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion", timeout=10)
        return [(str(t['id_tipo_innovacion']), t['name']) for t in response.json()]
    except Exception:
        return []

# Formulario migrado
class SolucionesForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=255)],
                         render_kw={'class': 'form-control', 'placeholder': 'Ingrese el título de la solución'})

    descripcion = TextAreaField('Descripción', validators=[DataRequired()],
                                render_kw={'class': 'form-control', 'placeholder': 'Proporcione una descripción detallada de la solución'})

    recursos_requeridos = IntegerField('Recursos Requeridos', validators=[DataRequired()],
                                       render_kw={'class': 'form-control', 'placeholder': 'Cantidad de recursos necesarios'})

    palabras_claves = StringField('Palabras Claves', validators=[DataRequired(), Length(max=255)],
                                  render_kw={'class': 'form-control', 'placeholder': 'Palabras clave relacionadas con la solución'})

    fecha_creacion = DateField('Fecha de Creación', validators=[DataRequired()], format='%Y-%m-%d',
                               render_kw={'class': 'form-control', 'type': 'date'})

    archivo_multimedia = FileField('Archivo Multimedia',
                                   validators=[Optional(), FileAllowed(ALLOWED_FILES, 'Formato no permitido')],
                                   render_kw={'class': 'form-control'})

    id_foco_innovacion = SelectField('Foco de Innovación', choices=[], coerce=str,
                                     validators=[DataRequired()], render_kw={'class': 'form-control'})

    id_tipo_innovacion = SelectField('Tipo de Innovación', choices=[], coerce=str,
                                     validators=[DataRequired()], render_kw={'class': 'form-control'})

    mensaje_experto = TextAreaField('Mensaje del Experto', validators=[Optional()],
                                    render_kw={'class': 'form-control', 'placeholder': 'Deja tu mensaje como experto aquí'})

    desarrollador_por = StringField('Desarrollado por', validators=[Optional(), Length(max=255)],
                                    render_kw={'class': 'form-control', 'placeholder': 'Equipo, persona, área, unidad'})

    area_unidad_desarrollo = StringField('Área o Unidad de Desarrollo', validators=[Optional(), Length(max=255)],
                                         render_kw={'class': 'form-control', 'placeholder': 'Área o unidad responsable'})

    def __init__(self, *args, **kwargs):
        super(SolucionesForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()
