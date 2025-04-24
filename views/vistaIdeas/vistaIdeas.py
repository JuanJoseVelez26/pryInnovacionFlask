# app/ideas/routes.py
import os
import json
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)
from werkzeug.utils import secure_filename
from .models import (
    APIClient, TipoInnovacionAPI, FocoInnovacionAPI,
    IdeaUsuario
)
from forms.formsIdeas.formsIdeas import IdeasForm 
from .utils import create_notification  # asumiendo que la tienes en utils.py

ideas_bp = Blueprint('ideas', __name__, template_folder='templates/ideas')

# helper para procesar fechas ISO y quedarnos sólo con YYYY-MM-DD
def _format_date(fecha_str):
    if not fecha_str:
        return None
    if fecha_str.endswith('Z'):
        fecha_str = fecha_str[:-1]
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return "Fecha inválida"

@ideas_bp.route('/ideas')
def list_ideas():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('auth.login'))

    client = APIClient('idea')
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # filtros
    tipo_sel = request.args.get('tipo_innovacion', '')
    foco_sel = request.args.get('foco_innovacion', '')
    estado_sel = request.args.get('estado', '')

    where = []
    if tipo_sel:
        where.append(f"id_tipo_innovacion = {tipo_sel}")
    if foco_sel:
        where.append(f"id_foco_innovacion = {foco_sel}")
    if estado_sel in ('True','False'):
        where.append(f"estado = {estado_sel.upper()}")

    where_clause = " AND ".join(where)

    try:
        ideas = client.get_data(where_condition=where_clause)
        # maps para nombres
        focos_map = {f['id_foco_innovacion']: f['name'] for f in focos}
        tipos_map = {t['id_tipo_innovacion']: t['name'] for t in tipos}
        for idea in ideas:
            idea['foco_nombre'] = focos_map.get(idea.get('id_foco_innovacion'), 'Desconocido')
            idea['tipo_nombre'] = tipos_map.get(idea.get('id_tipo_innovacion'), 'Desconocido')
            idea['fecha_creacion'] = _format_date(idea.get('fecha_creacion'))
        if not ideas:
            flash('No hay ideas disponibles.', 'info')
        else:
            flash(f'Se obtuvieron {len(ideas)} ideas.', 'info')
    except Exception as e:
        flash(f'Error al obtener las ideas: {e}', 'danger')
        ideas = []

    # comprobar rol
    perfil = APIClient('perfil').get_data(
        where_condition=f"usuario_email = '{user_email}'"
    )
    is_experto = bool(perfil and perfil[0].get('rol') == 'Experto')

    return render_template('ideas/list.html',
        ideas=ideas,
        focos=focos,
        tipos=tipos,
        selected_tipo=tipo_sel,
        selected_foco=foco_sel,
        selected_estado=estado_sel,
        is_experto=is_experto,
    )


@ideas_bp.route('/ideas/create', methods=['GET','POST'])
def create_idea():
    user_email = session.get('user_email')
    if not user_email:
        flash('Por favor, inicia sesión para crear una idea.', 'warning')
        return redirect(url_for('auth.login'))

    # traer focos y tipos
    try:
        focos = json.loads(APIClient('foco_innovacion').get_data()['result'][0]['result'])
        tipos = json.loads(APIClient('tipo_innovacion').get_data()['result'][0]['result'])
    except Exception:
        focos, tipos = [], []
        flash('Error al cargar focos o tipos de innovación.', 'danger')

    form = IdeasForm()
    if form.validate_on_submit():
        # preparar payload
        data = {
            'titulo': form.titulo.data,
            'descripcion': form.descripcion.data,
            'palabras_claves': form.palabras_claves.data,
            'recursos_requeridos': form.recursos_requeridos.data,
            'fecha_creacion': form.fecha_creacion.data.isoformat(),
            'id_foco_innovacion': int(form.id_foco_innovacion.data),
            'id_tipo_innovacion': int(form.id_tipo_innovacion.data),
            'creador_por': user_email
        }
        # archivo
        f = request.files.get('archivo_multimedia')
        if f:
            filename = secure_filename(f.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            path = os.path.join(upload_folder, filename)
            f.save(path)
            data['archivo_multimedia'] = filename

        try:
            resp = APIClient('idea').insert_data(json_data=data)
            # asumir éxito si no lanza excepción
            flash('¡Idea creada con éxito!', 'success')
            return redirect(url_for('ideas.list_ideas'))
        except Exception as e:
            flash(f'Error al crear la idea: {e}', 'danger')

    return render_template('ideas/create.html',
        form=form, focos=focos, tipos=tipos
    )


@ideas_bp.route('/ideas/<int:pk>/delete', methods=['GET','POST'])
def delete_idea(pk):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('auth.login'))

    client = APIClient('idea')
    ideas = client.get_data(where_condition=f"codigo_idea = {pk}")
    if not ideas:
        flash('Idea no encontrada.', 'warning')
        return redirect(url_for('ideas.list_ideas'))
    idea = ideas[0]

    # chequear rol experto
    perfil = APIClient('perfil').get_data(
        where_condition=f"usuario_email = '{user_email}'"
    )
    is_experto = bool(perfil and perfil[0].get('rol')=='Experto')

    if request.method == 'POST':
        try:
            client.delete_data(where_condition=f"codigo_idea = {pk}")
            # borrar archivo
            fn = idea.get('archivo_multimedia')
            if fn:
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
                if os.path.exists(path):
                    os.remove(path)
            # notificación
            create_notification(
                experto_email=user_email,
                tipo_entidad='idea',
                entidad_titulo=idea['titulo'],
                accion='eliminar',
                usuario_email=idea['creador_por'],
                mensaje_experto=request.form.get('mensaje_experto')
            )
            flash('Idea eliminada con éxito.', 'success')
            return redirect(url_for('ideas.list_ideas'))
        except Exception as e:
            flash(f'Error al eliminar la idea: {e}', 'danger')

    return render_template('ideas/delete.html',
        idea=idea, is_experto=is_experto
    )


@ideas_bp.route('/ideas/<int:codigo_idea>')
def detail_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('auth.login'))

    idea = IdeaUsuario.get_idea_by_codigo(codigo_idea)
    if not idea or 'codigo_idea' not in idea:
        flash('Idea no encontrada.', 'warning')
        return render_template('ideas/detail.html', idea=None)

    # nombres de tipo y foco
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()
    idea['tipo_nombre'] = next((t['name'] for t in tipos if t['id_tipo_innovacion']==idea['id_tipo_innovacion']), 'Desconocido')
    idea['foco_nombre'] = next((f['name'] for f in focos if f['id_foco_innovacion']==idea['id_foco_innovacion']), 'Desconocido')
    # URL multimedia
    fn = idea.get('archivo_multimedia')
    idea['archivo_url'] = url_for('static', filename='uploads/'+fn) if fn else None

    return render_template('ideas/detail.html', idea=idea)


@ideas_bp.route('/ideas/<int:pk>/edit', methods=['GET','POST'])
def update_idea(pk):
    user_email = session.get('user_email')
    if not user_email:
        flash('Por favor, inicia sesión para editar.', 'warning')
        return redirect(url_for('auth.login'))

    client = APIClient('idea')
    ideas = client.get_data(where_condition=f"codigo_idea = {pk}")
    if not ideas:
        flash('Idea no encontrada.', 'warning')
        return redirect(url_for('ideas.list_ideas'))
    idea = ideas[0]

    perfil = APIClient('perfil').get_data(
        where_condition=f"usuario_email = '{user_email}'"
    )
    is_experto = bool(perfil and perfil[0].get('rol')=='Experto')

    # focos/tipos
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    form = IdeasUpdateForm(data=idea)
    if not is_experto:
        del form.mensaje_experto

    if form.validate_on_submit():
        data = {
            'titulo': form.titulo.data,
            'descripcion': form.descripcion.data,
            'palabras_claves': form.palabras_claves.data,
            'recursos_requeridos': form.recursos_requeridos.data,
            'fecha_creacion': form.fecha_creacion.data.isoformat(),
            'id_foco_innovacion': int(form.id_foco_innovacion.data),
            'id_tipo_innovacion': int(form.id_tipo_innovacion.data),
            'creador_por': idea['creador_por']
        }
        # archivo
        f = request.files.get('archivo_multimedia')
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
            data['archivo_multimedia'] = filename
        else:
            data['archivo_multimedia'] = idea.get('archivo_multimedia')

        try:
            updated = client.auto_update_data(
                where_condition=f"codigo_idea = {pk}",
                json_data=data
            )
            if updated:
                create_notification(
                    experto_email=user_email,
                    tipo_entidad='idea',
                    entidad_titulo=idea['titulo'],
                    accion='actualizar',
                    usuario_email=idea['creador_por'],
                    mensaje_experto=form.mensaje_experto.data if is_experto else None
                )
                flash('Idea actualizada con éxito.', 'success')
            else:
                flash('No hubo cambios.', 'info')
            return redirect(url_for('ideas.list_ideas'))
        except Exception as e:
            flash(f'Error al actualizar la idea: {e}', 'danger')

    return render_template('ideas/update.html',
        form=form, focos=focos, tipos=tipos, is_experto=is_experto
    )


@ideas_bp.route('/ideas/<int:codigo_idea>/confirm', methods=['GET','POST'])
def confirmar_idea(codigo_idea):
    user_email = session.get('user_email')
    if not user_email:
        flash('Por favor, inicia sesión para confirmar.', 'warning')
        return redirect(url_for('auth.login'))

    perfil = APIClient('perfil').get_data(
        where_condition=f"usuario_email = '{user_email}'"
    )
    is_experto = bool(perfil and perfil[0].get('rol')=='Experto')

    client = APIClient('idea')
    ideas = client.get_data(where_condition=f"codigo_idea = {codigo_idea}")
    if not ideas:
        flash('Idea no encontrada.', 'warning')
        return redirect(url_for('ideas.list_ideas'))
    idea = ideas[0]

    if request.method == 'POST':
        try:
            # confirmar
            client.auto_update_data(
                where_condition=f"codigo_idea = {codigo_idea}",
                json_data={'estado': True}
            )
            # transferir a proyecto
            proyecto_data = {
                "tipo_origen": "idea",
                "id_origen": codigo_idea,
                "titulo": idea['titulo'],
                "descripcion": idea['descripcion'],
                "fecha_creacion": idea['fecha_creacion'],
                "palabras_claves": idea['palabras_claves'],
                "recursos_requeridos": idea['recursos_requeridos'],
                "archivo_multimedia": idea.get('archivo_multimedia'),
                "creador_por": idea['creador_por'],
                "id_tipo_innovacion": idea['id_tipo_innovacion'],
                "id_foco_innovacion": idea['id_foco_innovacion'],
                "estado": True,
                "fecha_aprobacion": datetime.utcnow().isoformat(),
                "aprobado_por": user_email,
            }
            APIClient('proyecto').insert_data(json_data=proyecto_data)
            flash('Idea confirmada y transferida a proyecto.', 'success')
            return redirect(url_for('ideas.list_ideas'))
        except Exception as e:
            flash(f'Error al confirmar la idea: {e}', 'danger')

    return render_template('ideas/confirmar_ideas.html',
        idea=idea, is_experto=is_experto
    )
