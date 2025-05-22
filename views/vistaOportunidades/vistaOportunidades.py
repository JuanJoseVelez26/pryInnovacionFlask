from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.api_client import APIClient
from config_flask import API_CONFIG
from forms.formsOportunidades.formsOportunidades import OportunidadForm

oportunidades_bp = Blueprint('oportunidades', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@oportunidades_bp.route('/oportunidades')
def list_oportunidades():
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para ver las oportunidades', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para ver las oportunidades', 'error')
            return redirect(url_for('login.login_view'))
            
        # Obtener datos
        oportunidades = api_client.get_oportunidades()
        
        # Crear formulario para obtener las opciones
        form = OportunidadForm()
        tipos = api_client.get_tipos_mercado() or []
        estados = api_client.get_estados() or []
        form.tipo_mercado.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
        
        return render_template('templatesOportunidades/list.html', 
                             oportunidades=oportunidades,
                             form=form)
    except Exception as e:
        flash(f'Error al cargar las oportunidades: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@oportunidades_bp.route('/oportunidades/<int:oportunidad_id>')
def view_oportunidad(oportunidad_id):
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para ver la oportunidad', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para ver la oportunidad', 'error')
            return redirect(url_for('login.login_view'))
            
        oportunidad = api_client.get_oportunidad(oportunidad_id)
        if not oportunidad:
            flash('Oportunidad no encontrada', 'error')
            return redirect(url_for('oportunidades.list_oportunidades'))
        
        # Crear formulario para obtener las opciones
        form = OportunidadForm()
        tipos = api_client.get_tipos_mercado() or []
        estados = api_client.get_estados() or []
        form.tipo_mercado.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
            
        return render_template('templatesOportunidades/view.html', 
                             oportunidad=oportunidad,
                             form=form)
    except Exception as e:
        flash(f'Error al cargar la oportunidad: {str(e)}', 'error')
        return redirect(url_for('oportunidades.list_oportunidades'))

@oportunidades_bp.route('/oportunidades/create', methods=['GET', 'POST'])
def create_oportunidad():
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para crear una oportunidad', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para crear una oportunidad', 'error')
            return redirect(url_for('login.login_view'))
            
        form = OportunidadForm()
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_mercado() or []
        estados = api_client.get_estados() or []
        form.tipo_mercado.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
        
        if form.validate_on_submit():
            oportunidad_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'tipo_mercado': form.tipo_mercado.data,
                'estado': form.estado.data,
                'usuario_email': user_email
            }
            
            response = api_client.create_oportunidad(oportunidad_data)
            if response:
                flash('Oportunidad creada exitosamente', 'success')
                return redirect(url_for('oportunidades.list_oportunidades'))
            else:
                flash('Error al crear la oportunidad', 'error')
                
        return render_template('templatesOportunidades/create.html', form=form)
    except Exception as e:
        flash(f'Error al crear la oportunidad: {str(e)}', 'error')
        return render_template('templatesOportunidades/create.html', form=form)

@oportunidades_bp.route('/oportunidades/<int:oportunidad_id>/edit', methods=['GET', 'POST'])
def update_oportunidad(oportunidad_id):
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para editar la oportunidad', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para editar la oportunidad', 'error')
            return redirect(url_for('login.login_view'))
            
        oportunidad = api_client.get_oportunidad(oportunidad_id)
        if not oportunidad:
            flash('Oportunidad no encontrada', 'error')
            return redirect(url_for('oportunidades.list_oportunidades'))
            
        form = OportunidadForm(obj=oportunidad)
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_mercado() or []
        estados = api_client.get_estados() or []
        form.tipo_mercado.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
        
        if form.validate_on_submit():
            oportunidad_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'tipo_mercado': form.tipo_mercado.data,
                'estado': form.estado.data
            }
            
            response = api_client.update_oportunidad(oportunidad_id, oportunidad_data)
            if response:
                flash('Oportunidad actualizada exitosamente', 'success')
                return redirect(url_for('oportunidades.view_oportunidad', oportunidad_id=oportunidad_id))
            else:
                flash('Error al actualizar la oportunidad', 'error')
                
        return render_template('templatesOportunidades/edit.html', form=form, oportunidad=oportunidad)
    except Exception as e:
        flash(f'Error al actualizar la oportunidad: {str(e)}', 'error')
        return render_template('templatesOportunidades/edit.html', form=form, oportunidad=oportunidad)

@oportunidades_bp.route('/oportunidades/<int:oportunidad_id>/delete', methods=['POST'])
def delete_oportunidad(oportunidad_id):
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para eliminar la oportunidad', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para eliminar la oportunidad', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.delete_oportunidad(oportunidad_id)
        if response:
            flash('Oportunidad eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la oportunidad', 'error')
            
        return redirect(url_for('oportunidades.list_oportunidades'))
    except Exception as e:
        flash(f'Error al eliminar la oportunidad: {str(e)}', 'error')
        return redirect(url_for('oportunidades.list_oportunidades'))

@oportunidades_bp.route('/oportunidades/<int:oportunidad_id>/confirmar', methods=['POST'])
def confirmar_oportunidad(oportunidad_id):
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        flash('Debe iniciar sesión para confirmar la oportunidad', 'error')
        return redirect(url_for('login.login_view'))
    try:
        user_email = session.get('user_email')
        if not user_email:
            flash('Debe iniciar sesión para confirmar la oportunidad', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.confirmar_oportunidad(oportunidad_id)
        if response:
            flash('Oportunidad confirmada exitosamente', 'success')
        else:
            flash('Error al confirmar la oportunidad', 'error')
            
        return redirect(url_for('oportunidades.view_oportunidad', oportunidad_id=oportunidad_id))
    except Exception as e:
        flash(f'Error al confirmar la oportunidad: {str(e)}', 'error')
        return redirect(url_for('oportunidades.list_oportunidades'))
