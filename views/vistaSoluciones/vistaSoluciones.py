from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.api_client import APIClient
from config_flask import API_CONFIG
from forms.formsSoluciones.formsSoluciones import SolucionForm

soluciones_bp = Blueprint('soluciones', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@soluciones_bp.route('/soluciones')
def list_soluciones():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver las soluciones', 'error')
            return redirect(url_for('login.login_view'))
            
        # Obtener filtros de la URL
        tipo_solucion = request.args.get('tipo_solucion')
        estado = request.args.get('estado')
        
        # Obtener datos
        soluciones = api_client.get_soluciones(tipo_solucion, estado)
        tipos = api_client.get_tipos_solucion()
        estados = api_client.get_estados()
        
        return render_template('templatesSoluciones/list.html', 
                             soluciones=soluciones,
                             tipos=tipos,
                             estados=estados)
    except Exception as e:
        flash(f'Error al cargar las soluciones: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@soluciones_bp.route('/soluciones/<int:solucion_id>')
def view_solucion(solucion_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver la solución', 'error')
            return redirect(url_for('login.login_view'))
            
        solucion = api_client.get_solucion(solucion_id)
        if not solucion:
            flash('Solución no encontrada', 'error')
            return redirect(url_for('soluciones.list_soluciones'))
            
        return render_template('templatesSoluciones/view.html', solucion=solucion)
    except Exception as e:
        flash(f'Error al cargar la solución: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/create', methods=['GET', 'POST'])
def create_solucion():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para crear una solución', 'error')
            return redirect(url_for('login.login_view'))
            
        form = SolucionForm()
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_solucion()
        estados = api_client.get_estados()
        form.tipo_solucion.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
        
        if form.validate_on_submit():
            solucion_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'tipo_solucion': form.tipo_solucion.data,
                'estado': form.estado.data,
                'usuario_id': user_id
            }
            
            response = api_client.create_solucion(solucion_data)
            if response:
                flash('Solución creada exitosamente', 'success')
                return redirect(url_for('soluciones.list_soluciones'))
            else:
                flash('Error al crear la solución', 'error')
                
        return render_template('templatesSoluciones/create.html', form=form)
    except Exception as e:
        flash(f'Error al crear la solución: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/<int:solucion_id>/edit', methods=['GET', 'POST'])
def update_solucion(solucion_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para editar la solución', 'error')
            return redirect(url_for('login.login_view'))
            
        solucion = api_client.get_solucion(solucion_id)
        if not solucion:
            flash('Solución no encontrada', 'error')
            return redirect(url_for('soluciones.list_soluciones'))
            
        form = SolucionForm(obj=solucion)
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_solucion()
        estados = api_client.get_estados()
        form.tipo_solucion.choices = [(t['id'], t['nombre']) for t in tipos]
        form.estado.choices = [(e['id'], e['nombre']) for e in estados]
        
        if form.validate_on_submit():
            solucion_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'tipo_solucion': form.tipo_solucion.data,
                'estado': form.estado.data
            }
            
            response = api_client.update_solucion(solucion_id, solucion_data)
            if response:
                flash('Solución actualizada exitosamente', 'success')
                return redirect(url_for('soluciones.view_solucion', solucion_id=solucion_id))
            else:
                flash('Error al actualizar la solución', 'error')
                
        return render_template('templatesSoluciones/edit.html', form=form, solucion=solucion)
    except Exception as e:
        flash(f'Error al actualizar la solución: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/<int:solucion_id>/delete', methods=['POST'])
def delete_solucion(solucion_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para eliminar la solución', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.delete_solucion(solucion_id)
        if response:
            flash('Solución eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la solución', 'error')
            
        return redirect(url_for('soluciones.list_soluciones'))
    except Exception as e:
        flash(f'Error al eliminar la solución: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/<int:solucion_id>/confirmar', methods=['POST'])
def confirmar_solucion(solucion_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para confirmar la solución', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.confirmar_solucion(solucion_id)
        if response:
            flash('Solución confirmada exitosamente', 'success')
        else:
            flash('Error al confirmar la solución', 'error')
            
        return redirect(url_for('soluciones.view_solucion', solucion_id=solucion_id))
    except Exception as e:
        flash(f'Error al confirmar la solución: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/calendario')
def calendario():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver el calendario', 'error')
            return redirect(url_for('login.login_view'))
            
        return render_template('templatesSoluciones/calendario.html')
    except Exception as e:
        flash(f'Error al cargar el calendario: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/ultimos-lanzamientos')
def ultimos_lanzamientos():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver los últimos lanzamientos', 'error')
            return redirect(url_for('login.login_view'))
            
        return render_template('templatesSoluciones/ultimos_lanzamientos.html')
    except Exception as e:
        flash(f'Error al cargar los últimos lanzamientos: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

@soluciones_bp.route('/soluciones/proximos-lanzamientos')
def proximos_lanzamientos():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver los próximos lanzamientos', 'error')
            return redirect(url_for('login.login_view'))
            
        return render_template('templatesSoluciones/proximos_lanzamientos.html')
    except Exception as e:
        flash(f'Error al cargar los próximos lanzamientos: {str(e)}', 'error')
        return redirect(url_for('soluciones.list_soluciones'))
