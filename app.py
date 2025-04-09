from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta segura
csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, email):
        self.id = email

# Usuario de ejemplo
users = {
    1: User(1)
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Definir la URL base de la API
API_BASE_URL = "http://190.217.58.246:5186/api/sgv"

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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Aquí deberías verificar las credenciales contra tu base de datos
        # Por ahora, usamos un usuario de ejemplo
        if email == "usuario@ejemplo.com" and password == "password":
            user = users[1]
            login_user(user)
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
    
    return render_template('templatesLogin/login.html')

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email')
        password = request.form.get('password')
        # TODO: Implementar el registro real de usuarios
        if email and password:
            flash('Registro exitoso')
            return redirect(url_for('login'))

    return render_template('templatesLogin/register.html')

# Ruta de perfil actualizada
@app.route('/perfil')
@login_required
def perfil():
    return render_template('templatesLogin/perfil.html', usuario=current_user)

# Ruta de logout actualizada
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('user_email', None)
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Endpoint para mostrar la lista de ideas con filtros
@app.route('/ideas', methods=['GET'])
@login_required
def lista_ideas():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
                              user_email=user_email,
                              is_experto=is_experto)
    except Exception as e:
        print(f"Error al obtener las ideas: {e}")
        flash("Error al cargar las ideas", "error")
        return render_template('templatesIdeas/list.html', ideas=[], tipos=[], focos=[])

@app.route('/ideas/create', methods=['GET', 'POST'])
@login_required
def create_idea():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
                "creador_por": user_email,
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
@login_required
def detail_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
@login_required
def update_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
        if idea['creador_por'] != user_email and not is_experto:
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
@login_required
def delete_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
        if idea['creador_por'] != user_email and not is_experto:
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
@login_required
def confirmar_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
@login_required
def dashboard():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
@login_required
def app_view():
    user_email = session.get('user_email')
    if not user_email:
        flash("Debes iniciar sesión para ver tus notificaciones.")
        return redirect(url_for('login'))

    api_client = APIClient("notificaciones")
    where_condition = f"usuario_email = '{user_email}'"
    notificaciones = api_client.get_data(where_condition=where_condition)

    if not notificaciones or not isinstance(notificaciones, list):
        flash("No se pudieron cargar las notificaciones.")
        notificaciones = []

    notificaciones = sorted(notificaciones, key=lambda x: x.get('leida', True))
    return render_template('templatesAuthentication/app.html', notificaciones=notificaciones)

@app.route('/marcar_leida', methods=['POST'])
@login_required
def marcar_leida():
    notificacion_id = request.form.get('id')
    if notificacion_id:
        api_client = APIClient("notificaciones")
        where_condition = f"id = {notificacion_id}"
        json_data = {"leida": True}
        response = api_client.update_data(where_condition=where_condition, json_data=json_data)
        
        if response:
            flash("Notificación marcada como leída.")
        else:
            flash("No se pudo marcar como leída. Intenta nuevamente.")
    else:
        flash("ID de notificación no válido.")
    
    return redirect(url_for('app_view'))

@app.route('/eliminar_notificacion', methods=['POST'])
@login_required
def eliminar_notificacion():
    notificacion_id = request.form.get('id')
    if notificacion_id:
        api_client = APIClient("notificaciones")
        where_condition = f"id = {notificacion_id}"
        response = api_client.delete_data(where_condition=where_condition)
        
        if response:
            flash("Notificación eliminada correctamente.")
        else:
            flash("No se pudo eliminar la notificación. Intenta nuevamente.")
    else:
        flash("ID de notificación no válido.")
    
    return redirect(url_for('app_view'))

@app.route('/listar_proyectos')
@login_required
def listar_proyectos():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
@login_required
def lista_ideas_view():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
    try:
        client = APIClient('idea')
        ideas = client.get_data()
        return render_template('templatesAuthentication/lista_ideas.html', ideas=ideas)
    except Exception as e:
        print(f"Error al obtener las ideas: {e}")
        return render_template('templatesAuthentication/lista_ideas.html', ideas=[])

@app.route('/lista_opportunities')
@login_required
def lista_opportunities():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
    try:
        client = APIClient('oportunidad')
        oportunidades = client.get_data()
        return render_template('templatesAuthentication/lista_opportunities.html', oportunidades=oportunidades)
    except Exception as e:
        print(f"Error al obtener las oportunidades: {e}")
        return render_template('templatesAuthentication/lista_opportunities.html', oportunidades=[])

@app.route('/lista_solutions')
@login_required
def lista_solutions():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
    try:
        client = APIClient('solucion')
        soluciones = client.get_data()
        return render_template('templatesAuthentication/lista_solutions.html', soluciones=soluciones)
    except Exception as e:
        print(f"Error al obtener las soluciones: {e}")
        return render_template('templatesAuthentication/lista_solutions.html', soluciones=[])

# Rutas para crear ideas y oportunidades
@app.route('/create_idea')
@login_required
def create_idea_view():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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
@login_required
def create_opportunity():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
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

    def get_data(self, select_columns=None, where_condition=None):
        # TODO: Implementar la lógica real de la API
        # Por ahora retornamos datos de ejemplo
        if self.table_name == "notificaciones":
            return [
                {"id": 1, "mensaje": "Notificación de ejemplo", "leida": False},
                {"id": 2, "mensaje": "Otra notificación", "leida": True}
            ]
        elif self.table_name == "idea":
            return [{"titulo": "Idea 1"}, {"titulo": "Idea 2"}]
        elif self.table_name == "oportunidad":
            return [{"titulo": "Oportunidad 1"}, {"titulo": "Oportunidad 2"}]
        elif self.table_name == "solucion":
            return [{"titulo": "Solución 1"}, {"titulo": "Solución 2"}]
        elif self.table_name == "usuario":
            return [{"email": "usuario1@example.com"}, {"email": "usuario2@example.com"}]
        return []

    def update_data(self, where_condition, json_data):
        # TODO: Implementar la lógica real de actualización
        return True

    def delete_data(self, where_condition):
        # TODO: Implementar la lógica real de eliminación
        return True

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

