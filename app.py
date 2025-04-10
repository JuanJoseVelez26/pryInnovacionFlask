from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from config_flask import *
import mysql.connector
from werkzeug.security import generate_password_hash
from passlib.hash import pbkdf2_sha256
from forms.formsLogin.forms import LoginForm, RegisterForm
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object('config_flask')
csrf = CSRFProtect(app)

# Configuración de la base de datos
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'innovacion_db')
}

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.nombre = user_data.get('nombre', '')
        self.apellido = user_data.get('apellido', '')
        self.rol = user_data.get('rol', '')
        self.fecha_nacimiento = user_data.get('fecha_nacimiento', '')
        self.direccion = user_data.get('direccion', '')
        self.descripcion = user_data.get('descripcion', '')
        self.area_expertise = user_data.get('area_expertise', '')
        self.info_adicional = user_data.get('info_adicional', '')

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Error al cargar usuario: {e}")
        return None

# Definir la URL base de la API
API_BASE_URL = API_URL

# Funciones para obtener datos desde la API
def obtener_focos_innovacion():
    response = requests.get(f"{API_BASE_URL}/foco_innovacion")
    return response.json() if response.status_code == 200 else []

def obtener_tipos_innovacion():
    response = requests.get(f"{API_BASE_URL}/tipo_innovacion")
    return response.json() if response.status_code == 200 else []

def obtener_ideas(filtro_tipo=None, filtro_foco=None, filtro_estado=None):
    params = {}
    if filtro_tipo:
        params["tipo_innovacion"] = filtro_tipo
    if filtro_foco:
        params["foco_innovacion"] = filtro_foco
    if filtro_estado is not None:
        params["estado"] = filtro_estado

    response = requests.get(f"{API_BASE_URL}/ideas", params=params)
    return response.json() if response.status_code == 200 else []

# Página de inicio
@app.route('/')
def home():
    return render_template('templatesAuthentication/home.html')

# Alias para la página de inicio
@app.route('/index')
def index():
    return home()

# Ruta de login actualizada
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Comentado temporalmente para permitir acceso sin login
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
        
    # form = LoginForm()
    # if form.validate_on_submit():
    #     try:
    #         # Intentar autenticación directa con la base de datos como respaldo
    #         conn = mysql.connector.connect(**db_config)
    #         cursor = conn.cursor(dictionary=True)
            
    #         # Verificar credenciales
    #         cursor.execute("SELECT * FROM usuario WHERE email = %s", (form.email.data,))
    #         user_data = cursor.fetchone()
            
    #         if user_data:
    #             # Verificar la contraseña usando passlib
    #             stored_password = user_data['password']
    #             if stored_password.startswith('pbkdf2_sha256$'):
    #                 # Si la contraseña está hasheada con pbkdf2_sha256 (formato Django)
    #                 if pbkdf2_sha256.verify(form.password.data, stored_password):
    #                     # Obtener datos de perfil
    #                     cursor.execute("""
    #                         SELECT p.*, u.email, u.rol 
    #                         FROM perfil p 
    #                         JOIN usuario u ON p.usuario_email = u.email 
    #                         WHERE u.email = %s
    #                     """, (form.email.data,))
    #                     profile = cursor.fetchone()
                        
    #                     if not profile:
    #                         flash("No se encontraron datos de perfil para el usuario.", "error")
    #                         return render_template('templatesLogin/login.html', form=form)
                        
    #                     # Convertir fecha de nacimiento si está presente
    #                     fecha_nacimiento = profile.get('fecha_nacimiento', '')
    #                     if fecha_nacimiento:
    #                         try:
    #                             fecha_nacimiento = datetime.strptime(str(fecha_nacimiento), "%Y-%m-%d")
    #                             fecha_nacimiento = fecha_nacimiento.strftime("%d/%m/%Y")
    #                         except ValueError:
    #                             fecha_nacimiento = None
                        
    #                     # Crear objeto de usuario
    #                     user = User(user_data)
                        
    #                     # Almacenar datos en sesión
    #                     session['user_email'] = user.email
    #                     session['user_name'] = profile.get('nombre', '')
    #                     session['user_role'] = profile.get('rol', '')
    #                     session['user_birthdate'] = fecha_nacimiento
    #                     session['user_address'] = profile.get('direccion', '')
    #                     session['user_description'] = profile.get('descripcion', '')
    #                     session['user_area_expertise'] = profile.get('area_expertise', '')
    #                     session['user_info_adicional'] = profile.get('info_adicional', '')
                        
    #                     # Actualizar last_login en la base de datos
    #                     cursor.execute("""
    #                         UPDATE usuario 
    #                         SET last_login = %s 
    #                         WHERE email = %s
    #                     """, (datetime.now(), form.email.data))
    #                     conn.commit()
                        
    #                     # Iniciar sesión
    #                     login_user(user)
    #                     flash('Has iniciado sesión exitosamente', 'success')
    #                     return redirect(url_for('dashboard'))
    #             else:
    #                 # Intentar con werkzeug si no es pbkdf2_sha256
    #                 from werkzeug.security import check_password_hash
    #                 if check_password_hash(stored_password, form.password.data):
    #                     # Obtener datos de perfil
    #                     cursor.execute("""
    #                         SELECT p.*, u.email, u.rol 
    #                         FROM perfil p 
    #                         JOIN usuario u ON p.usuario_email = u.email 
    #                         WHERE u.email = %s
    #                     """, (form.email.data,))
    #                     profile = cursor.fetchone()
                        
    #                     if not profile:
    #                         flash("No se encontraron datos de perfil para el usuario.", "error")
    #                         return render_template('templatesLogin/login.html', form=form)
                        
    #                     # Convertir fecha de nacimiento si está presente
    #                     fecha_nacimiento = profile.get('fecha_nacimiento', '')
    #                     if fecha_nacimiento:
    #                         try:
    #                             fecha_nacimiento = datetime.strptime(str(fecha_nacimiento), "%Y-%m-%d")
    #                             fecha_nacimiento = fecha_nacimiento.strftime("%d/%m/%Y")
    #                         except ValueError:
    #                             fecha_nacimiento = None
                        
    #                     # Crear objeto de usuario
    #                     user = User(user_data)
                        
    #                     # Almacenar datos en sesión
    #                     session['user_email'] = user.email
    #                     session['user_name'] = profile.get('nombre', '')
    #                     session['user_role'] = profile.get('rol', '')
    #                     session['user_birthdate'] = fecha_nacimiento
    #                     session['user_address'] = profile.get('direccion', '')
    #                     session['user_description'] = profile.get('descripcion', '')
    #                     session['user_area_expertise'] = profile.get('area_expertise', '')
    #                     session['user_info_adicional'] = profile.get('info_adicional', '')
                        
    #                     # Actualizar last_login en la base de datos
    #                     cursor.execute("""
    #                         UPDATE usuario 
    #                         SET last_login = %s 
    #                         WHERE email = %s
    #                     """, (datetime.now(), form.email.data))
    #                     conn.commit()
                        
    #                     # Iniciar sesión
    #                     login_user(user)
    #                     flash('Has iniciado sesión exitosamente', 'success')
    #                     return redirect(url_for('dashboard'))
            
    #         flash('Correo electrónico o contraseña inválidos', 'error')
    #     except mysql.connector.Error as e:
    #         print(f"Error de base de datos: {e}")
    #         flash('Error al conectar con la base de datos', 'error')
    #     except Exception as e:
    #         print(f"Error en login: {e}")
    #         flash('Error al intentar iniciar sesión', 'error')
    #     finally:
    #         if 'cursor' in locals() and cursor:
    #             cursor.close()
    #         if 'conn' in locals() and conn:
    #             conn.close()
    
    # Redirigir directamente al dashboard sin autenticación
    return redirect(url_for('dashboard'))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Comentado temporalmente para permitir acceso sin login
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
        
    # form = RegisterForm()
    # if form.validate_on_submit():
    #     try:
    #         conn = mysql.connector.connect(**db_config)
    #         cursor = conn.cursor(dictionary=True)
            
    #         # Verificar si el email ya existe
    #         cursor.execute("SELECT * FROM usuario WHERE email = %s", (form.email.data,))
    #         if cursor.fetchone():
    #             flash('El email ya está registrado', 'error')
    #             return render_template('templatesLogin/register.html', form=form)
            
    #         # Crear usuario
    #         hashed_password = generate_password_hash(form.password1.data)
    #         cursor.execute("""
    #             INSERT INTO usuario (email, password, is_active, is_staff)
    #             VALUES (%s, %s, %s, %s)
    #         """, (form.email.data, hashed_password, True, False))
            
    #         # Crear perfil
    #         cursor.execute("""
    #             INSERT INTO perfil (
    #                 usuario_email, nombre, fecha_nacimiento, direccion,
    #                 descripcion, area_expertise, info_adicional
    #             ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    #         """, (
    #             form.email.data, form.nombre.data, form.fecha_nacimiento.data,
    #             form.direccion.data, form.descripcion.data,
    #             form.area_expertise.data, form.informacion_adicional.data
    #         ))
            
    #         conn.commit()
    #         flash('Registro exitoso. Por favor inicia sesión.', 'success')
    #         return redirect(url_for('login'))
            
    #     except Exception as e:
    #         print(f"Error en registro: {e}")
    #         flash('Error al registrar usuario', 'error')
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    
    # Redirigir directamente al dashboard sin autenticación
    return redirect(url_for('dashboard'))

# Ruta de perfil actualizada
@app.route('/perfil')
# @login_required
def perfil():
    # Comentado temporalmente para permitir acceso sin login
    # return render_template('templatesLogin/perfil.html', usuario=current_user)
    return render_template('templatesLogin/perfil.html')

# Ruta de logout actualizada
@app.route('/logout', methods=['POST'])
# @login_required
def logout():
    # Comentado temporalmente para permitir acceso sin login
    # logout_user()
    # session.clear()
    # flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Endpoint para mostrar la lista de ideas con filtros
@app.route('/ideas', methods=['GET'])
# @login_required
def lista_ideas():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener parámetros de filtrado
        tipo_innovacion = request.args.get('tipo_innovacion')
        foco_innovacion = request.args.get('foco_innovacion')
        estado = request.args.get('estado')
        
        # Obtener datos de la API
        ideas_client = APIClient("idea")
        tipos_client = APIClient("tipo_innovacion")
        focos_client = APIClient("foco_innovacion")
        
        # Construir condiciones de filtrado
        where_conditions = []
        if tipo_innovacion:
            where_conditions.append(f"id_tipo_innovacion = {tipo_innovacion}")
        if foco_innovacion:
            where_conditions.append(f"id_foco_innovacion = {foco_innovacion}")
        if estado:
            where_conditions.append(f"estado = {estado}")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else None
        
        # Obtener datos
        ideas = ideas_client.get_data(where_condition=where_clause)
        tipos = tipos_client.get_data()
        focos = focos_client.get_data()
        
        # Verificar si el usuario es experto
        is_experto = False  # Aquí deberías implementar la lógica para verificar si el usuario es experto
        
        return render_template('templatesIdeas/list.html', 
                              ideas=ideas, 
                              tipos=tipos, 
                              focos=focos, 
                              selected_tipo=tipo_innovacion,
                              selected_foco=foco_innovacion,
                              selected_estado=estado,
                              user_email="usuario@ejemplo.com",  # Usuario ficticio para desarrollo
                              is_experto=is_experto)
    except Exception as e:
        print(f"Error al obtener las ideas: {e}")
        flash("Error al cargar las ideas", "error")
        return render_template('templatesIdeas/list.html', ideas=[], tipos=[], focos=[])

@app.route('/ideas/create', methods=['GET', 'POST'])
# @login_required
def create_idea():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            palabras_claves = request.form.get('palabras_claves')
            recursos_requeridos = request.form.get('recursos_requeridos')
            fecha_creacion = request.form.get('fecha_creacion')
            id_foco_innovacion = request.form.get('id_foco_innovacion')
            id_tipo_innovacion = request.form.get('id_tipo_innovacion')
            
            # Manejar archivo multimedia
            archivo_multimedia = request.files.get('archivo_multimedia')
            archivo_multimedia_path = None
            
            if archivo_multimedia and archivo_multimedia.filename:
                # Aquí deberías implementar la lógica para guardar el archivo
                # Por ejemplo:
                # filename = secure_filename(archivo_multimedia.filename)
                # archivo_multimedia_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # archivo_multimedia.save(archivo_multimedia_path)
                pass
            
            # Crear idea en la API
            ideas_client = APIClient("idea")
            idea_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "palabras_claves": palabras_claves,
                "recursos_requeridos": recursos_requeridos,
                "fecha_creacion": fecha_creacion,
                "archivo_multimedia": archivo_multimedia_path,
                "id_foco_innovacion": id_foco_innovacion,
                "id_tipo_innovacion": id_tipo_innovacion,
                "creador_por": "usuario@ejemplo.com",  # Usuario ficticio para desarrollo
                "estado": False  # Por defecto, la idea está pendiente
            }
            
            response = ideas_client.create_data(json_data=idea_data)
            
            if response:
                flash("Idea creada exitosamente", "success")
                return redirect(url_for('lista_ideas'))
            else:
                flash("Error al crear la idea", "error")
        except Exception as e:
            print(f"Error al crear la idea: {e}")
            flash("Error al crear la idea", "error")
    
    # Si es GET o hubo un error en POST, mostrar el formulario
    try:
        tipos_client = APIClient("tipo_innovacion")
        focos_client = APIClient("foco_innovacion")
        
        tipos = tipos_client.get_data()
        focos = focos_client.get_data()
        
        return render_template('templatesIdeas/create.html', tipos=tipos, focos=focos)
    except Exception as e:
        print(f"Error al cargar el formulario: {e}")
        flash("Error al cargar el formulario", "error")
        return redirect(url_for('lista_ideas'))

@app.route('/ideas/<int:codigo_idea>', methods=['GET'])
# @login_required
def detail_idea(codigo_idea):
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener datos de la idea
        ideas_client = APIClient("idea")
        where_condition = f"codigo_idea = {codigo_idea}"
        ideas = ideas_client.get_data(where_condition=where_condition)
        
        if not ideas:
            flash("Idea no encontrada", "error")
            return redirect(url_for('lista_ideas'))
        
        idea = ideas[0]
        
        # Obtener datos de tipo y foco de innovación
        tipos_client = APIClient("tipo_innovacion")
        focos_client = APIClient("foco_innovacion")
        
        tipos = tipos_client.get_data()
        focos = focos_client.get_data()
        
        # Encontrar el tipo y foco correspondientes
        tipo_innovacion = next((t for t in tipos if t['id_tipo_innovacion'] == idea['id_tipo_innovacion']), None)
        foco_innovacion = next((f for f in focos if f['id_foco_innovacion'] == idea['id_foco_innovacion']), None)
        
        return render_template('templatesIdeas/detail.html', 
                              idea=idea, 
                              tipo_innovacion=tipo_innovacion['name'] if tipo_innovacion else "No especificado",
                              foco_innovacion=foco_innovacion['name'] if foco_innovacion else "No especificado")
    except Exception as e:
        print(f"Error al obtener el detalle de la idea: {e}")
        flash("Error al cargar el detalle de la idea", "error")
        return redirect(url_for('lista_ideas'))

@app.route('/ideas/<int:codigo_idea>/update', methods=['GET', 'POST'])
# @login_required
def update_idea(codigo_idea):
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener datos de la idea
        ideas_client = APIClient("idea")
        where_condition = f"codigo_idea = {codigo_idea}"
        ideas = ideas_client.get_data(where_condition=where_condition)
        
        if not ideas:
            flash("Idea no encontrada", "error")
            return redirect(url_for('lista_ideas'))
        
        idea = ideas[0]
        
        # Verificar si el usuario es el creador o un experto
        is_experto = False  # Aquí deberías implementar la lógica para verificar si el usuario es experto
        if idea['creador_por'] != "usuario@ejemplo.com" and not is_experto:  # Usuario ficticio para desarrollo
            flash("No tiene permiso para editar esta idea", "error")
            return redirect(url_for('lista_ideas'))
        
        if request.method == 'POST':
            # Obtener datos del formulario
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            palabras_claves = request.form.get('palabras_claves')
            recursos_requeridos = request.form.get('recursos_requeridos')
            fecha_creacion = request.form.get('fecha_creacion')
            id_foco_innovacion = request.form.get('id_foco_innovacion')
            id_tipo_innovacion = request.form.get('id_tipo_innovacion')
            
            # Manejar archivo multimedia
            archivo_multimedia = request.files.get('archivo_multimedia')
            archivo_multimedia_path = idea.get('archivo_multimedia')
            
            if archivo_multimedia and archivo_multimedia.filename:
                # Aquí deberías implementar la lógica para guardar el archivo
                # Por ejemplo:
                # filename = secure_filename(archivo_multimedia.filename)
                # archivo_multimedia_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # archivo_multimedia.save(archivo_multimedia_path)
                pass
            
            # Actualizar idea en la API
            idea_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "palabras_claves": palabras_claves,
                "recursos_requeridos": recursos_requeridos,
                "fecha_creacion": fecha_creacion,
                "archivo_multimedia": archivo_multimedia_path,
                "id_foco_innovacion": id_foco_innovacion,
                "id_tipo_innovacion": id_tipo_innovacion
            }
            
            response = ideas_client.update_data(where_condition=where_condition, json_data=idea_data)
            
            if response:
                flash("Idea actualizada exitosamente", "success")
                return redirect(url_for('lista_ideas'))
            else:
                flash("Error al actualizar la idea", "error")
        
        # Si es GET o hubo un error en POST, mostrar el formulario
        tipos_client = APIClient("tipo_innovacion")
        focos_client = APIClient("foco_innovacion")
        
        tipos = tipos_client.get_data()
        focos = focos_client.get_data()
        
        # Crear un formulario con los datos de la idea
        form_data = {
            "titulo": idea.get('titulo', ''),
            "descripcion": idea.get('descripcion', ''),
            "palabras_claves": idea.get('palabras_claves', ''),
            "recursos_requeridos": idea.get('recursos_requeridos', ''),
            "fecha_creacion": idea.get('fecha_creacion', ''),
            "id_foco_innovacion": idea.get('id_foco_innovacion', ''),
            "id_tipo_innovacion": idea.get('id_tipo_innovacion', '')
        }
        
        return render_template('templatesIdeas/update.html', 
                              form=form_data, 
                              tipos=tipos, 
                              focos=focos)
    except Exception as e:
        print(f"Error al actualizar la idea: {e}")
        flash("Error al actualizar la idea", "error")
        return redirect(url_for('lista_ideas'))

@app.route('/ideas/<int:codigo_idea>/delete', methods=['GET', 'POST'])
# @login_required
def delete_idea(codigo_idea):
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener datos de la idea
        ideas_client = APIClient("idea")
        where_condition = f"codigo_idea = {codigo_idea}"
        ideas = ideas_client.get_data(where_condition=where_condition)
        
        if not ideas:
            flash("Idea no encontrada", "error")
            return redirect(url_for('lista_ideas'))
        
        idea = ideas[0]
        
        # Verificar si el usuario es el creador o un experto
        is_experto = False  # Aquí deberías implementar la lógica para verificar si el usuario es experto
        if idea['creador_por'] != "usuario@ejemplo.com" and not is_experto:  # Usuario ficticio para desarrollo
            flash("No tiene permiso para eliminar esta idea", "error")
            return redirect(url_for('lista_ideas'))
        
        if request.method == 'POST':
            # Obtener mensaje del experto si existe
            mensaje_experto = request.form.get('mensaje_experto')
            
            # Eliminar idea de la API
            response = ideas_client.delete_data(where_condition=where_condition)
            
            if response:
                flash("Idea eliminada exitosamente", "success")
                return redirect(url_for('lista_ideas'))
            else:
                flash("Error al eliminar la idea", "error")
        
        # Si es GET, mostrar el formulario de confirmación
        return render_template('templatesIdeas/delete.html', 
                              idea=idea, 
                              is_experto=is_experto)
    except Exception as e:
        print(f"Error al eliminar la idea: {e}")
        flash("Error al eliminar la idea", "error")
        return redirect(url_for('lista_ideas'))

@app.route('/ideas/<int:codigo_idea>/confirmar', methods=['GET', 'POST'])
# @login_required
def confirmar_idea(codigo_idea):
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Verificar si el usuario es experto
        is_experto = False  # Aquí deberías implementar la lógica para verificar si el usuario es experto
        if not is_experto:
            flash("No tiene permiso para confirmar ideas", "error")
            return redirect(url_for('lista_ideas'))
        
        # Obtener datos de la idea
        ideas_client = APIClient("idea")
        where_condition = f"codigo_idea = {codigo_idea}"
        ideas = ideas_client.get_data(where_condition=where_condition)
        
        if not ideas:
            flash("Idea no encontrada", "error")
            return redirect(url_for('lista_ideas'))
        
        idea = ideas[0]
        
        if request.method == 'POST':
            # Obtener mensaje del experto si existe
            mensaje_experto = request.form.get('mensaje_experto')
            
            # Actualizar estado de la idea en la API
            idea_data = {
                "estado": True  # Marcar como aprobada
            }
            
            response = ideas_client.update_data(where_condition=where_condition, json_data=idea_data)
            
            if response:
                flash("Idea confirmada exitosamente", "success")
                return redirect(url_for('lista_ideas'))
            else:
                flash("Error al confirmar la idea", "error")
        
        # Si es GET, mostrar el formulario de confirmación
        return render_template('templatesIdeas/confirmar_ideas.html', 
                              idea=idea, 
                              mensaje_experto=None)
    except Exception as e:
        print(f"Error al confirmar la idea: {e}")
        flash("Error al confirmar la idea", "error")
        return redirect(url_for('lista_ideas'))

# Nuevos endpoints para las plantillas HTML proporcionadas

@app.route('/base')
def base_template():
    """
    Endpoint para renderizar la plantilla base.html
    """
    return render_template('base.html')

@app.route('/calendar')
def calendar():
    """
    Endpoint para renderizar la plantilla calendar.html
    """
    return render_template('calendar.html')

@app.route('/layouts-light-sidebar')
def layouts_light_sidebar():
    """
    Endpoint para renderizar la plantilla layouts-light-sidebar.html
    """
    return render_template('layouts-light-sidebar.html')

@app.route('/menu')
def menu():
    """
    Endpoint para renderizar la plantilla menu.html
    """
    return render_template('menu.html')

@app.route('/dashboard')
# @login_required
def dashboard():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        ideas_client = APIClient("idea")
        oportunidades_client = APIClient("oportunidad")
        solucion_client = APIClient("solucion")
        usuario_client = APIClient("usuario")

        ideas_data = ideas_client.get_data(select_columns="titulo")
        oportunidades_data = oportunidades_client.get_data(select_columns="titulo")
        solucion_data = solucion_client.get_data(select_columns="titulo")
        usuario_data = usuario_client.get_data(select_columns="email")

        ideas_count = len(ideas_data) if ideas_data else 0
        oportunidades_count = len(oportunidades_data) if oportunidades_data else 0
        solucion_count = len(solucion_data) if solucion_data else 0
        usuario_count = len(usuario_data) if usuario_data else 0

        context = {
            'ideas_count': ideas_count,
            'oportunidades_count': oportunidades_count,
            'solucion_count': solucion_count,
            'usuario_count': usuario_count,
            'now': datetime.now()
        }
        return render_template('templatesAuthentication/dashboard.html', **context)
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return render_template('templatesAuthentication/dashboard.html', 
                             ideas_count=0, oportunidades_count=0, 
                             solucion_count=0, usuario_count=0, now=datetime.now())

@app.route('/app')
# @login_required
def app_view():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     flash("Debes iniciar sesión para ver tus notificaciones.")
    #     return redirect(url_for('login'))

    # api_client = APIClient("notificaciones")
    # where_condition = f"usuario_email = '{user_email}'"
    # notificaciones = api_client.get_data(where_condition=where_condition)

    # if not notificaciones or not isinstance(notificaciones, list):
    #     flash("No se pudieron cargar las notificaciones.")
    #     notificaciones = []

    # notificaciones = sorted(notificaciones, key=lambda x: x.get('leida', True))
    # return render_template('templatesAuthentication/app.html', notificaciones=notificaciones)
    
    # Datos ficticios para desarrollo
    notificaciones = [
        {"id": 1, "titulo": "Notificación de prueba", "mensaje": "Esta es una notificación de prueba", "fecha": datetime.now(), "leida": False},
        {"id": 2, "titulo": "Otra notificación", "mensaje": "Esta es otra notificación de prueba", "fecha": datetime.now(), "leida": True}
    ]
    return render_template('templatesAuthentication/app.html', notificaciones=notificaciones)

@app.route('/marcar_leida', methods=['POST'])
# @login_required
def marcar_leida():
    # Comentado temporalmente para permitir acceso sin login
    # notificacion_id = request.form.get('id')
    # if notificacion_id:
    #     api_client = APIClient("notificaciones")
    #     where_condition = f"id = {notificacion_id}"
    #     json_data = {"leida": True}
    #     response = api_client.update_data(where_condition=where_condition, json_data=json_data)
        
    #     if response:
    #         flash("Notificación marcada como leída.")
    #     else:
    #         flash("No se pudo marcar como leída. Intenta nuevamente.")
    # else:
    #     flash("ID de notificación no válido.")
    
    flash("Notificación marcada como leída.")
    return redirect(url_for('app_view'))

@app.route('/eliminar_notificacion', methods=['POST'])
# @login_required
def eliminar_notificacion():
    # Comentado temporalmente para permitir acceso sin login
    # notificacion_id = request.form.get('id')
    # if notificacion_id:
    #     api_client = APIClient("notificaciones")
    #     where_condition = f"id = {notificacion_id}"
    #     response = api_client.delete_data(where_condition=where_condition)
        
    #     if response:
    #         flash("Notificación eliminada correctamente.")
    #     else:
    #         flash("No se pudo eliminar la notificación. Intenta nuevamente.")
    # else:
    #     flash("ID de notificación no válido.")
    
    flash("Notificación eliminada correctamente.")
    return redirect(url_for('app_view'))

@app.route('/listar_proyectos')
# @login_required
def listar_proyectos():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        client = APIClient('proyecto')
        proyectos = client.get_data()
        
        ideas = [p for p in proyectos if p.get('tipo_origen') == 'idea']
        oportunidades = [p for p in proyectos if p.get('tipo_origen') == 'oportunidad']
        soluciones = [p for p in proyectos if p.get('tipo_origen') == 'solución']
        
        return render_template('templatesAuthentication/listar_proyectos.html',
                             ideas=ideas, oportunidades=oportunidades, soluciones=soluciones)
    except Exception as e:
        print(f"Error al obtener los proyectos: {e}")
        return render_template('templatesAuthentication/listar_proyectos.html', 
                             ideas=[], oportunidades=[], soluciones=[])

@app.route('/lista_ideas')
# @login_required
def lista_ideas_view():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        client = APIClient('idea')
        ideas = client.get_data()
        return render_template('templatesAuthentication/lista_ideas.html', ideas=ideas)
    except Exception as e:
        print(f"Error al obtener las ideas: {e}")
        return render_template('templatesAuthentication/lista_ideas.html', ideas=[])

@app.route('/lista_opportunities')
# @login_required
def lista_opportunities():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        client = APIClient('oportunidad')
        oportunidades = client.get_data()
        return render_template('templatesAuthentication/lista_opportunities.html', oportunidades=oportunidades)
    except Exception as e:
        print(f"Error al obtener las oportunidades: {e}")
        return render_template('templatesAuthentication/lista_opportunities.html', oportunidades=[])

@app.route('/lista_solutions')
# @login_required
def lista_solutions():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        client = APIClient('solucion')
        soluciones = client.get_data()
        return render_template('templatesAuthentication/lista_solutions.html', soluciones=soluciones)
    except Exception as e:
        print(f"Error al obtener las soluciones: {e}")
        return render_template('templatesAuthentication/lista_solutions.html', soluciones=[])

# Rutas para crear ideas y oportunidades
@app.route('/create_idea')
# @login_required
def create_idea_view():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener tipos y focos de innovación para el formulario
        tipos = obtener_tipos_innovacion()
        focos = obtener_focos_innovacion()
        return render_template('templatesAuthentication/create_idea.html', tipos=tipos, focos=focos)
    except Exception as e:
        print(f"Error al cargar el formulario de creación de ideas: {e}")
        flash("Error al cargar el formulario de creación de ideas", "error")
        return redirect(url_for('lista_ideas'))

@app.route('/create_opportunity')
# @login_required
def create_opportunity():
    # Comentado temporalmente para permitir acceso sin login
    # user_email = session.get('user_email')
    # if not user_email:
    #     return redirect(url_for('login'))
    
    try:
        # Obtener tipos y focos de innovación para el formulario
        tipos = obtener_tipos_innovacion()
        focos = obtener_focos_innovacion()
        return render_template('templatesAuthentication/create_opportunity.html', tipos=tipos, focos=focos)
    except Exception as e:
        print(f"Error al cargar el formulario de creación de oportunidades: {e}")
        flash("Error al cargar el formulario de creación de oportunidades", "error")
        return redirect(url_for('lista_opportunities'))

# Clase APIClient para manejar las llamadas a la API
class APIClient:
    def __init__(self, table_name):
        self.table_name = table_name
        self.base_url = API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_data(self, select_columns=None, where_condition=None):
        try:
            payload = {
                "procedure": "select_json_entity",
                "parameters": {
                    "table_name": self.table_name,
                    "select_columns": select_columns if select_columns else "*",
                    "where_condition": where_condition if where_condition else None
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('outputParams', {}).get('result', [])
            else:
                print(f"Error en la petición: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {str(e)}")
            return []

    def update_data(self, where_condition, json_data):
        try:
            payload = {
                "procedure": "update_json_entity",
                "parameters": {
                    "table_name": self.table_name,
                    "set_columns": json_data,
                    "where_condition": where_condition
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {str(e)}")
            return False

    def delete_data(self, where_condition):
        try:
            payload = {
                "procedure": "delete_json_entity",
                "parameters": {
                    "table_name": self.table_name,
                    "where_condition": where_condition
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {str(e)}")
            return False

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

