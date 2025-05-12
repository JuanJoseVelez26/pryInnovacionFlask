from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from datetime import datetime
from models.AuthenticationModel import DatabaseModel, AuthenticationModel
from models.ideaModel import IdeaModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/notificaciones')
# @login_required
def notificaciones():
    try:
        # Inicializar modelo
        db_model = DatabaseModel('notificacion')
        
        # Obtener notificaciones
        notificaciones = db_model.execute_query("""
            SELECT *
            FROM notificacion
            WHERE usuario_email = %s
            ORDER BY fecha_creacion DESC
        """, (current_user.email,))
        
        # Marcar notificaciones como leídas
        db_model.execute_query("""
            UPDATE notificacion
            SET leida = TRUE
            WHERE usuario_email = %s AND leida = FALSE
        """, (current_user.email,), commit=True)
        
        return render_template('templatesAuthentication/notificaciones.html',
                             notificaciones=notificaciones)
    except Exception as e:
        flash(f'Error al cargar las notificaciones: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))

@auth_bp.route('/configuracion', methods=['GET', 'POST'])
# @login_required
def configuracion():
    # Inicializar modelo
    auth_model = AuthenticationModel()
    
    if request.method == 'POST':
        try:
            if current_user.is_anonymous:
                flash('Debes iniciar sesión para ver el dashboard', 'danger')
                return redirect(url_for('login.login_view'))
            
            # Actualizar configuración
            data = {
                'notificaciones_email': 'email' in request.form,
                'notificaciones_push': 'push' in request.form
            }
            
            if auth_model.update(data, "email = %s", (current_user.email,)):
                flash('Configuración actualizada exitosamente', 'success')
            else:
                flash('Error al actualizar la configuración', 'danger')
                
            return redirect(url_for('auth.configuracion'))
        except Exception as e:
            flash(f'Error al actualizar la configuración: {str(e)}', 'danger')
    
    try:
        # Obtener configuración actual
        config = auth_model.select(
            columns="notificaciones_email, notificaciones_push",
            where="email = %s",
            params=(current_user.email,),
            fetch_one=True
        )
        
        return render_template('templatesAuthentication/configuracion.html',
                             configuracion=config)
    except Exception as e:
        flash(f'Error al cargar la configuración: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))
