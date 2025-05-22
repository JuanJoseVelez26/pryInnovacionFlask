from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.api_client import APIClient

procedure_bp = Blueprint('procedure', __name__)
api_client = APIClient()

@procedure_bp.route('/procedures')
def show_procedures():
    """Muestra la lista de procedimientos"""
    try:
        procedures = api_client.get_procedures()
        return render_template('procedures/index.html', procedures=procedures)
    except Exception as e:
        flash(f'Error al cargar los procedimientos: {str(e)}', 'error')
        return render_template('procedures/index.html', procedures=[])

@procedure_bp.route('/procedures/new', methods=['GET', 'POST'])
def new_procedure():
    """Crea un nuevo procedimiento"""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'type': request.form['type'],
                'parameters': request.form.getlist('parameters[]')
            }
            api_client.create_procedure(data)
            flash('Procedimiento creado exitosamente', 'success')
            return redirect(url_for('procedure.show_procedures'))
        except Exception as e:
            flash(f'Error al crear el procedimiento: {str(e)}', 'error')
    return render_template('procedures/new.html')

@procedure_bp.route('/procedures/<int:id>/edit', methods=['GET', 'POST'])
def edit_procedure(id):
    """Edita un procedimiento existente"""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'type': request.form['type'],
                'parameters': request.form.getlist('parameters[]')
            }
            api_client.update_procedure(f'id = {id}', data)
            flash('Procedimiento actualizado exitosamente', 'success')
            return redirect(url_for('procedure.show_procedures'))
        except Exception as e:
            flash(f'Error al actualizar el procedimiento: {str(e)}', 'error')
    
    try:
        procedure = api_client.get_procedures(where_condition=f'id = {id}')
        if procedure:
            return render_template('procedures/edit.html', procedure=procedure[0])
        flash('Procedimiento no encontrado', 'error')
        return redirect(url_for('procedure.show_procedures'))
    except Exception as e:
        flash(f'Error al cargar el procedimiento: {str(e)}', 'error')
        return redirect(url_for('procedure.show_procedures'))

@procedure_bp.route('/procedures/<int:id>/delete', methods=['POST'])
def delete_procedure(id):
    """Elimina un procedimiento"""
    try:
        api_client.delete_procedure(f'id = {id}')
        flash('Procedimiento eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el procedimiento: {str(e)}', 'error')
    return redirect(url_for('procedure.show_procedures')) 