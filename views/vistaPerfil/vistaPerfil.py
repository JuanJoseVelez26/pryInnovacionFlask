from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.api_client import APIClient
from config_flask import API_CONFIG
from forms.formsPerfil.formsPerfil import PerfilForm

perfil_bp = Blueprint('perfil', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@perfil_bp.route('/perfil')
def view_perfil():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para ver su perfil', 'error')
            return redirect(url_for('login.login'))
            
        perfil = api_client.get_user_profile(user_id)
        if not perfil:
            flash('No se pudo cargar el perfil', 'error')
            return redirect(url_for('dashboard.index'))
            
        return render_template('perfil/view.html', perfil=perfil)
    except Exception as e:
        flash(f'Error al cargar el perfil: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@perfil_bp.route('/perfil/edit', methods=['GET', 'POST'])
def edit_perfil():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para editar su perfil', 'error')
            return redirect(url_for('login.login'))
            
        perfil = api_client.get_user_profile(user_id)
        if not perfil:
            flash('No se pudo cargar el perfil', 'error')
            return redirect(url_for('dashboard.index'))
            
        form = PerfilForm(obj=perfil)
        
        if form.validate_on_submit():
            data = {
                'nombre': form.nombre.data,
                'apellido': form.apellido.data,
                'email': form.email.data,
                'telefono': form.telefono.data,
                'cargo': form.cargo.data,
                'area': form.area.data
            }
            
            if form.password.data:
                data['password'] = form.password.data
                
            api_client.update_user_profile(user_id, data)
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('perfil.view_perfil'))
            
        return render_template('perfil/edit.html', form=form, perfil=perfil)
    except Exception as e:
        flash(f'Error al actualizar el perfil: {str(e)}', 'error')
        return redirect(url_for('perfil.view_perfil'))

@perfil_bp.route('/perfil/change-password', methods=['GET', 'POST'])
def change_password():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Debe iniciar sesión para cambiar su contraseña', 'error')
            return redirect(url_for('login.login'))
            
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return redirect(url_for('perfil.change_password'))
                
            data = {
                'current_password': current_password,
                'new_password': new_password
            }
            
            api_client.change_password(user_id, data)
            flash('Contraseña actualizada exitosamente', 'success')
            return redirect(url_for('perfil.view_perfil'))
            
        return render_template('perfil/change_password.html')
    except Exception as e:
        flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
        return redirect(url_for('perfil.view_perfil'))
