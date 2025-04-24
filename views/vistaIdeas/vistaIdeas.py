from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
# from flask_login import login_required, current_user
import mysql.connector
from datetime import datetime
from config_flask import DATABASE_CONFIG
from forms.formsIdeas.formsIdeas import IdeasForm
from forms.formsIdeas.forms import IdeaForm

# Usar la configuración de MySQL
db_config = DATABASE_CONFIG['mysql']

ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('/ideas')
# @login_required
def list_ideas():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Construir la consulta base
        query = """
            SELECT i.*, u.nombre as autor_nombre, ti.nombre as tipo_innovacion_nombre, fi.nombre as foco_innovacion_nombre
            FROM idea i
            JOIN usuario u ON i.usuario_email = u.email
            JOIN tipo_innovacion ti ON i.id_tipo_innovacion = ti.id_tipo_innovacion
            JOIN foco_innovacion fi ON i.id_foco_innovacion = fi.id_foco_innovacion
        """
        filters = []
        params = []

        # Aplicar filtros si existen
        tipo_innovacion = request.args.get('tipo_innovacion')
        foco_innovacion = request.args.get('foco_innovacion')
        estado = request.args.get('estado')

        if tipo_innovacion:
            filters.append("i.id_tipo_innovacion = %s")
            params.append(tipo_innovacion)
        if foco_innovacion:
            filters.append("i.id_foco_innovacion = %s")
            params.append(foco_innovacion)
        if estado is not None and estado != '':
             # Convertir estado a booleano adecuado para la base de datos (ej: 0 o 1)
            try:
                estado_bool = int(estado) # Asume 0 para pendiente, 1 para aprobado
                filters.append("i.estado = %s")
                params.append(estado_bool)
            except ValueError:
                flash('Valor de estado inválido.', 'warning')

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY i.fecha_creacion DESC"

        cursor.execute(query, tuple(params))
        ideas = cursor.fetchall()
        
        # Obtener tipos y focos para los filtros
        cursor.execute("SELECT * FROM tipo_innovacion")
        tipos = cursor.fetchall()
        
        cursor.execute("SELECT * FROM foco_innovacion")
        focos = cursor.fetchall()
        
        # Formatear fechas
        for idea in ideas:
            idea['fecha_creacion'] = idea['fecha_creacion'].strftime('%d/%m/%Y %H:%M') if idea['fecha_creacion'] else None
            idea['fecha_modificacion'] = idea['fecha_modificacion'].strftime('%d/%m/%Y %H:%M') if idea['fecha_modificacion'] else None
        
        return render_template('templatesIdeas/list.html', 
                             ideas=ideas, 
                             tipos=tipos, 
                             focos=focos,
                             selected_tipo=tipo_innovacion,
                             selected_foco=foco_innovacion,
                             selected_estado=estado,
                             user_email=session.get('email'),
                             is_experto=session.get('rol') == 'Experto')

    except Exception as e:
        flash(f'Error al cargar las ideas: {str(e)}', 'danger')
        # Renderizar la plantilla incluso si hay error, pero sin datos o con datos vacíos controlados
        return render_template('templatesIdeas/list.html',
                             ideas=[],
                             tipos=[],
                             focos=[],
                             selected_tipo=request.args.get('tipo_innovacion'),
                             selected_foco=request.args.get('foco_innovacion'),
                             selected_estado=request.args.get('estado'),
                             user_email=session.get('email'),
                             is_experto=session.get('rol') == 'Experto')
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    
    return render_template('templatesIdeas/list.html', ideas=ideas)

@ideas_bp.route('/ideas/<int:codigo_idea>')
# @login_required
def view_idea(codigo_idea):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT i.*, u.nombre as autor_nombre, ti.nombre as tipo_innovacion_nombre, fi.nombre as foco_innovacion_nombre
            FROM idea i
            JOIN usuario u ON i.usuario_email = u.email
            JOIN tipo_innovacion ti ON i.id_tipo_innovacion = ti.id_tipo_innovacion
            JOIN foco_innovacion fi ON i.id_foco_innovacion = fi.id_foco_innovacion
            WHERE i.codigo_idea = %s
        """, (codigo_idea,))
        idea = cursor.fetchone()
        
        if not idea:
            flash('Idea no encontrada', 'danger')
            return redirect(url_for('ideas.list_ideas'))
            
        # Formatear fechas
        idea['fecha_creacion'] = idea['fecha_creacion'].strftime('%d/%m/%Y %H:%M') if idea['fecha_creacion'] else None
        idea['fecha_modificacion'] = idea['fecha_modificacion'].strftime('%d/%m/%Y %H:%M') if idea['fecha_modificacion'] else None
        
        # Obtener el email del usuario de la sesión
        user_email = session.get('email')
        is_owner = idea['usuario_email'] == user_email
        is_experto = session.get('rol') == 'Experto'

        return render_template('templatesIdeas/detail.html', 
                            idea=idea,
                            is_owner=is_owner,
                            is_experto=is_experto)

    except Exception as e:
        flash(f'Error al cargar la idea: {str(e)}', 'danger')
        return redirect(url_for('ideas.list_ideas'))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@ideas_bp.route('/ideas/create', methods=['GET', 'POST'])
# @login_required
def create_idea():
    # Usar un email temporal si no hay sesión
    user_email = session.get('email', 'usuario@ejemplo.com')

    form = IdeaForm()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor_tipos = conn.cursor(dictionary=True)
        cursor_tipos.execute("SELECT id_tipo_innovacion as id, nombre FROM tipo_innovacion")
        tipos_innovacion = cursor_tipos.fetchall()
        cursor_tipos.close()

        cursor_focos = conn.cursor(dictionary=True)
        cursor_focos.execute("SELECT id_foco_innovacion as id, nombre FROM foco_innovacion")
        focos_innovacion = cursor_focos.fetchall()
        cursor_focos.close()
        conn.close() # Cerrar conexión después de obtener tipos y focos

        # Asignar las opciones a los campos SelectField del formulario
        form.id_tipo_innovacion.choices = [(t['id'], t['nombre']) for t in tipos_innovacion]
        form.id_foco_innovacion.choices = [(f['id'], f['nombre']) for f in focos_innovacion]

    except Exception as e:
        flash(f'Error al cargar datos para el formulario: {str(e)}', 'danger')
        tipos_innovacion = []
        focos_innovacion = []
        # Asegurarse de que choices no sea None si hay error
        form.id_tipo_innovacion.choices = []
        form.id_foco_innovacion.choices = []

    if form.validate_on_submit():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO idea (titulo, descripcion, palabras_claves, recursos_requeridos,
                id_tipo_innovacion, id_foco_innovacion, usuario_email, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.titulo.data,
                form.descripcion.data,
                form.palabras_claves.data,
                form.recursos_requeridos.data,
                form.id_tipo_innovacion.data,
                form.id_foco_innovacion.data,
                user_email, # Usar el email de la sesión o el temporal
                0 # Estado pendiente por defecto
            ))
            
            conn.commit()
            flash('Idea creada exitosamente', 'success')
            return redirect(url_for('ideas.list_ideas'))
            
        except Exception as e:
            flash(f'Error al crear la idea: {str(e)}', 'danger')
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    # Si no es POST o falla la validación/inserción, renderizar el formulario
    return render_template('templatesIdeas/create.html',
                         form=form,
                         tipos_innovacion=tipos_innovacion, # Pasar tipos y focos aunque ya estén en form.choices
                         focos_innovacion=focos_innovacion)

@ideas_bp.route('/ideas/<int:codigo_idea>/update', methods=['GET', 'POST'])
# @login_required
def update_idea(codigo_idea):
    user_email = session.get('email', 'usuario@ejemplo.com') # Email temporal o de sesión
    form = IdeasForm() # Asume que IdeasForm es para la actualización

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Obtener idea para verificar propietario y rellenar formulario
        cursor.execute("SELECT * FROM idea WHERE codigo_idea = %s", (codigo_idea,))
        idea = cursor.fetchone()

        if not idea:
            flash('Idea no encontrada.', 'danger')
            return redirect(url_for('ideas.list_ideas'))

        # Verificar si el usuario es el propietario (usando email de sesión o temporal)
        if idea['usuario_email'] != user_email:
            flash('No tienes permiso para editar esta idea.', 'danger')
            return redirect(url_for('ideas.list_ideas'))

        # Obtener tipos y focos para los selects
        cursor.execute("SELECT id_tipo_innovacion as id, nombre FROM tipo_innovacion")
        tipos_innovacion = cursor.fetchall()
        form.id_tipo_innovacion.choices = [(t['id'], t['nombre']) for t in tipos_innovacion]

        cursor.execute("SELECT id_foco_innovacion as id, nombre FROM foco_innovacion")
        focos_innovacion = cursor.fetchall()
        form.id_foco_innovacion.choices = [(f['id'], f['nombre']) for f in focos_innovacion]

        if request.method == 'POST' and form.validate_on_submit():
            # Actualizar la idea en la base de datos
            update_cursor = conn.cursor()
            update_cursor.execute("""
                UPDATE idea SET
                    titulo = %s, descripcion = %s, palabras_claves = %s,
                    recursos_requeridos = %s, id_tipo_innovacion = %s, id_foco_innovacion = %s,
                    fecha_modificacion = %s
                WHERE codigo_idea = %s AND usuario_email = %s
            """, (
                form.titulo.data, form.descripcion.data, form.palabras_claves.data,
                form.recursos_requeridos.data, form.id_tipo_innovacion.data, form.id_foco_innovacion.data,
                datetime.now(), codigo_idea, user_email
            ))
            conn.commit()
            update_cursor.close()
            flash('Idea actualizada exitosamente.', 'success')
            return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))

        elif request.method == 'GET':
            # Rellenar el formulario con los datos existentes
            form.titulo.data = idea['titulo']
            form.descripcion.data = idea['descripcion']
            form.palabras_claves.data = idea['palabras_claves']
            form.recursos_requeridos.data = idea['recursos_requeridos']
            form.id_tipo_innovacion.data = idea['id_tipo_innovacion']
            form.id_foco_innovacion.data = idea['id_foco_innovacion']

        # Si es GET o la validación falla, mostrar el formulario
        return render_template('templatesIdeas/update.html', form=form, idea=idea)

    except Exception as e:
        flash(f'Error al procesar la actualización: {str(e)}', 'danger')
        # Podrías redirigir o renderizar el template con un mensaje de error
        return redirect(url_for('ideas.list_ideas')) # Redirigir en caso de error grave
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@ideas_bp.route('/ideas/<int:codigo_idea>/delete', methods=['POST'])
# @login_required
def delete_idea(codigo_idea):
    user_email = session.get('email', 'usuario@ejemplo.com') # Usar email temporal si no hay sesión

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True) # Usar dictionary=True para facilitar la verificación

        # Primero, verificar si la idea existe y si el usuario es el propietario
        cursor.execute("SELECT usuario_email FROM idea WHERE codigo_idea = %s", (codigo_idea,))
        idea = cursor.fetchone()

        if not idea:
            flash('Idea no encontrada.', 'danger')
            return redirect(url_for('ideas.list_ideas'))

        if idea['usuario_email'] != user_email:
            flash('No tienes permiso para eliminar esta idea.', 'danger')
            return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))

        # Si es el propietario, proceder a eliminar
        delete_cursor = conn.cursor()
        delete_cursor.execute("DELETE FROM idea WHERE codigo_idea = %s", (codigo_idea,))
        conn.commit()
        delete_cursor.close()

        flash('Idea eliminada exitosamente', 'success')
        return redirect(url_for('ideas.list_ideas'))

    except Exception as e:
        flash(f'Error al eliminar la idea: {str(e)}', 'danger')
        # Redirigir a la vista de la idea si falla la eliminación pero la verificación pasó
        return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@ideas_bp.route('/ideas/<int:codigo_idea>/confirmar', methods=['POST'])
# @login_required
def confirmar_idea(codigo_idea):
    user_email = session.get('email', 'usuario@ejemplo.com')
    user_rol = session.get('rol') # Obtener rol de la sesión

    # Si no hay rol en la sesión, asumir un rol que no sea Experto para seguridad
    if not user_rol:
         user_rol = 'Usuario' # O cualquier rol por defecto no privilegiado

    if user_rol != 'Experto':
        flash('No tienes permiso para confirmar ideas.', 'danger')
        return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Actualizar estado de la idea
        cursor.execute("""
            UPDATE idea SET estado = 1, fecha_modificacion = %s
            WHERE codigo_idea = %s
        """, (datetime.now(), codigo_idea))

        # Crear proyecto a partir de la idea (ajustar según tu esquema de 'proyecto')
        # Asegúrate de que la tabla 'proyecto' y sus columnas existan
        cursor.execute("""
            INSERT INTO proyecto (titulo, descripcion, palabras_claves, recursos_requeridos,
                                  fecha_creacion, id_tipo_innovacion, id_foco_innovacion,
                                  creador_por, estado, fecha_aprobacion, aprobado_por, id_idea)
            SELECT titulo, descripcion, palabras_claves, recursos_requeridos,
                   fecha_creacion, id_tipo_innovacion, id_foco_innovacion,
                   usuario_email, 1, %s, %s, codigo_idea
            FROM idea WHERE codigo_idea = %s
        """, (datetime.now(), user_email, codigo_idea))

        conn.commit()
        flash('Idea confirmada y proyecto creado exitosamente.', 'success')

    except mysql.connector.Error as err:
         flash(f'Error de base de datos al confirmar la idea: {err}', 'danger')
    except Exception as e:
        flash(f'Error inesperado al confirmar la idea: {str(e)}', 'danger')
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    return redirect(url_for('ideas.list_ideas')) # Redirige siempre al final

@ideas_bp.route('/ideas/matriz-evaluacion')
# @login_required
def matriz_evaluacion():
    return render_template('templatesIdeas/matriz_evaluacion.html')

@ideas_bp.route('/ideas/estadisticas')
# @login_required
def estadisticas():
    # Aquí podrías añadir lógica para obtener y pasar datos de estadísticas
    return render_template('templatesIdeas/estadisticas.html')

@ideas_bp.route('/ideas/retos')
# @login_required
def retos():
    # Lógica para mostrar retos
    return render_template('templatesIdeas/retos.html')

@ideas_bp.route('/ideas/top-generadores')
# @login_required
def top_generadores():
    # Lógica para obtener y mostrar el top 10
    return render_template('templatesIdeas/top_generadores.html')

@ideas_bp.route('/ideas/evaluacion')
# @login_required
def evaluacion():
    # Lógica para la evaluación de ideas
    return render_template('templatesIdeas/evaluacion.html')

@ideas_bp.route('/ideas/mercado')
# @login_required
def mercado():
    # Lógica para el mercado de ideas
    return render_template('templatesIdeas/mercado.html')