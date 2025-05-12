from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed
import requests

# Funciones para cargar opciones desde las APIs
def obtener_focos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion", timeout=10)
        return [(str(foco['id_foco_innovacion']), foco['name']) for foco in response.json()]
    except:
        return []

def obtener_tipos_innovacion():
    try:
        response = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion", timeout=10)
        return [(str(tipo['id_tipo_innovacion']), tipo['name']) for tipo in response.json()]
    except:
        return []

class SolucionesUpdateForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=255)],
                         render_kw={"class": "form-control", "placeholder": "Ingrese el título de la solución"})

    descripcion = TextAreaField('Descripción', validators=[DataRequired()],
                                render_kw={"class": "form-control", "placeholder": "Proporcione una descripción detallada de la solución"})

    recursos_requeridos = IntegerField('Recursos Requeridos', validators=[DataRequired()],
                                       render_kw={"class": "form-control", "placeholder": "Cantidad de recursos necesarios"})

    palabras_claves = StringField('Palabras Claves', validators=[DataRequired(), Length(max=255)],
                                  render_kw={"class": "form-control", "placeholder": "Palabras clave relacionadas con la solución"})

    fecha_creacion = DateField('Fecha de Creación', validators=[DataRequired()],
                               format='%Y-%m-%d',
                               render_kw={"class": "form-control", "type": "date"})

    archivo_multimedia = FileField('Archivos Multimedia',
                                   render_kw={"class": "form-control"},
                                   validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'mp4', 'avi'], 'Solo se permiten archivos multimedia.')])

    id_foco_innovacion = SelectField('Foco de Innovación', choices=[], coerce=str,
                                     render_kw={"class": "form-control"})

    id_tipo_innovacion = SelectField('Tipo de Innovación', choices=[], coerce=str,
                                     render_kw={"class": "form-control"})

    mensaje_experto = TextAreaField('Mensaje del Experto',
                                    render_kw={"class": "form-control", "placeholder": "Deja tu mensaje como experto aquí"},
                                    default='')

    desarrollador_por = StringField('Desarrollado por', render_kw={"class": "form-control", "placeholder": "Equipo, persona, área, unidad"})

    area_unidad_desarrollo = StringField('Área o Unidad de Desarrollo', render_kw={"class": "form-control", "placeholder": "Área o unidad responsable"})

    def __init__(self, *args, **kwargs):
        super(SolucionesUpdateForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()

class SolucionesForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=255)],
                         render_kw={"class": "form-control", "placeholder": "Ingrese el título de la solución"})

    descripcion = TextAreaField('Descripción', validators=[DataRequired()],
                                render_kw={"class": "form-control", "placeholder": "Proporcione una descripción detallada de la solución"})

    recursos_requeridos = IntegerField('Recursos Requeridos', validators=[DataRequired()],
                                       render_kw={"class": "form-control", "placeholder": "Cantidad de recursos necesarios"})

    palabras_claves = StringField('Palabras Claves', validators=[DataRequired(), Length(max=255)],
                                  render_kw={"class": "form-control", "placeholder": "Palabras clave relacionadas con la solución"})

    fecha_creacion = DateField('Fecha de Creación', validators=[DataRequired()],
                               format='%Y-%m-%d',
                               render_kw={"class": "form-control", "type": "date"})

    archivo_multimedia = FileField('Archivos Multimedia',
                                   render_kw={"class": "form-control"},
                                   validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'mp4', 'avi'], 'Solo se permiten archivos multimedia.')])

    id_foco_innovacion = SelectField('Foco de Innovación', choices=[], coerce=str,
                                     render_kw={"class": "form-control"})

    id_tipo_innovacion = SelectField('Tipo de Innovación', choices=[], coerce=str,
                                     render_kw={"class": "form-control"})

    creador_por = StringField('Creado por', render_kw={"class": "form-control", "placeholder": "Nombre del creador"})

    desarrollador_por = StringField('Desarrollado por', render_kw={"class": "form-control", "placeholder": "Equipo, persona, área, unidad"})

    area_unidad_desarrollo = StringField('Área o Unidad de Desarrollo', render_kw={"class": "form-control", "placeholder": "Área o unidad responsable"})

    def __init__(self, *args, **kwargs):
        super(SolucionesForm, self).__init__(*args, **kwargs)
        self.id_foco_innovacion.choices = obtener_focos_innovacion()
        self.id_tipo_innovacion.choices = obtener_tipos_innovacion()

class SolucionForm(FlaskForm):
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
    
    tipo_innovacion = SelectField('Tipo de Innovación', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un tipo de innovación')
    ])
    
    foco_innovacion = SelectField('Foco de Innovación', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un foco de innovación')
    ])
    
    submit = SubmitField('Guardar')
