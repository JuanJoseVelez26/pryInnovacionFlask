from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.AuthenticationModel import AuthenticationModel
from forms.formsPerfil.forms import RegisterForm
from datetime import datetime

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Inicializar el modelo de autenticación
            auth_model = AuthenticationModel()
            
            # Crear usuario
            user = auth_model.create_user(
                email=form.email.data,
                password=form.password.data,
                is_active=True,  # Activar usuario inmediatamente
                is_staff=False
            )
            
            if user:
                # Datos del perfil
                perfil_data = {
                    'nombre': form.nombre.data,
                    'rol': 'Usuario',  # Rol por defecto
                    'fecha_nacimiento': form.fecha_nacimiento.data.strftime('%Y-%m-%d') if form.fecha_nacimiento.data else None,
                    'direccion': form.direccion.data,
                    'descripcion': form.descripcion.data,
                    'area_expertise': form.area_expertise.data,
                    'info_adicional': form.info_adicional.data
                }
                
                # Actualizar perfil
                if auth_model.update(perfil_data, "email = %s", (user['email'],)):
                    flash('Usuario registrado exitosamente. Por favor inicia sesión.', 'success')
                    return redirect(url_for('login.login_view'))
                else:
                    # Si falla la actualización del perfil, eliminar el usuario
                    auth_model.delete("email = %s", (user['email'],))
                    flash('Error al crear el perfil del usuario.', 'danger')
            else:
                flash('Error al crear el usuario.', 'danger')
                
        except Exception as e:
            flash(f'Error durante el registro: {str(e)}', 'danger')
    
    return render_template('login/register.html', form=form)