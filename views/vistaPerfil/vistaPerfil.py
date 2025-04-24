from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_required, current_user
import mysql.connector
from config_flask import DATABASE_CONFIG
from forms.formsPerfil.forms import PerfilForm

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil')
# @login_required
def mi_perfil():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, u.email
            FROM perfil p
            JOIN usuario u ON p.usuario_email = u.email
            WHERE p.usuario_email = %s
        """, ('usuario@ejemplo.com',))  # Email temporal
        perfil = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not perfil:
            flash('Perfil no encontrado', 'danger')
            return redirect(url_for('auth.dashboard'))
            
        return render_template('templatesPerfil/mi_perfil.html', perfil=perfil)
    except Exception as e:
        flash(f'Error al cargar el perfil: {str(e)}', 'danger')
        return redirect(url_for('auth.dashboard'))

@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
# @login_required
def editar_perfil():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, u.email
            FROM perfil p
            JOIN usuario u ON p.usuario_email = u.email
            WHERE p.usuario_email = %s
        """, ('usuario@ejemplo.com',))  # Email temporal
        perfil = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not perfil:
            flash('Perfil no encontrado', 'danger')
            return redirect(url_for('auth.dashboard'))
            
        form = PerfilForm(obj=perfil)
        if form.validate_on_submit():
            try:
                conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE perfil
                    SET nombre = %s,
                        fecha_nacimiento = %s,
                        direccion = %s,
                        descripcion = %s,
                        area_expertise = %s,
                        info_adicional = %s
                    WHERE usuario_email = %s
                """, (
                    form.nombre.data,
                    form.fecha_nacimiento.data,
                    form.direccion.data,
                    form.descripcion.data,
                    form.area_expertise.data,
                    form.info_adicional.data,
                    'usuario@ejemplo.com'  # Email temporal
                ))
                conn.commit()
                cursor.close()
                conn.close()
                
                flash('Perfil actualizado exitosamente', 'success')
                return redirect(url_for('perfil.mi_perfil'))
            except Exception as e:
                flash(f'Error al actualizar el perfil: {str(e)}', 'danger')
        
        return render_template('templatesPerfil/editar_perfil.html', form=form, perfil=perfil)
    except Exception as e:
        flash(f'Error al cargar el perfil: {str(e)}', 'danger')
        return redirect(url_for('auth.dashboard'))

@perfil_bp.route('/perfil/cambiar-password', methods=['GET', 'POST'])
# @login_required
def cambiar_password():
    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT password FROM usuario
                WHERE email = %s
            """, ('usuario@ejemplo.com',))  # Email temporal
            usuario = cursor.fetchone()
            
            if not usuario:
                flash('Usuario no encontrado', 'danger')
                return redirect(url_for('auth.dashboard'))
                
            if request.form['password_actual'] != usuario['password']:
                flash('Contraseña actual incorrecta', 'danger')
                return redirect(url_for('perfil.cambiar_password'))
                
            if request.form['nueva_password'] != request.form['confirmar_password']:
                flash('Las contraseñas no coinciden', 'danger')
                return redirect(url_for('perfil.cambiar_password'))
                
            cursor.execute("""
                UPDATE usuario
                SET password = %s
                WHERE email = %s
            """, (request.form['nueva_password'], 'usuario@ejemplo.com'))  # Email temporal
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Contraseña actualizada exitosamente', 'success')
            return redirect(url_for('perfil.mi_perfil'))
        except Exception as e:
            flash(f'Error al cambiar la contraseña: {str(e)}', 'danger')
    
    return render_template('templatesPerfil/cambiar_password.html')
