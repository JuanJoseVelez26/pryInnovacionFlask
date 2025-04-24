from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import mysql.connector
from werkzeug.security import generate_password_hash
from passlib.hash import pbkdf2_sha256
from forms.formsLogin.forms import LoginForm, RegisterForm
from config_flask import DATABASE_CONFIG

# Usar la configuración de MySQL
db_config = DATABASE_CONFIG['mysql']

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM usuario WHERE email = %s", (form.email.data,))
            user_data = cursor.fetchone()
            
            if user_data:
                stored_password = user_data['password']
                if stored_password.startswith('pbkdf2_sha256$'):
                    if pbkdf2_sha256.verify(form.password.data, stored_password):
                        cursor.execute("""
                            SELECT p.*, u.email, u.rol 
                            FROM perfil p 
                            JOIN usuario u ON p.usuario_email = u.email 
                            WHERE u.email = %s
                        """, (form.email.data,))
                        profile = cursor.fetchone()
                        
                        if not profile:
                            flash("No se encontraron datos de perfil para el usuario.", "error")
                            return render_template('templatesLogin/login.html', form=form)
                        
                        fecha_nacimiento = profile.get('fecha_nacimiento', '')
                        if fecha_nacimiento:
                            try:
                                fecha_nacimiento = datetime.strptime(str(fecha_nacimiento), "%Y-%m-%d")
                                fecha_nacimiento = fecha_nacimiento.strftime("%d/%m/%Y")
                            except ValueError:
                                fecha_nacimiento = None
                        
                        user = User(user_data)
                        
                        session['user_email'] = user.email
                        session['user_name'] = profile.get('nombre', '')
                        session['user_role'] = profile.get('rol', '')
                        session['user_birthdate'] = fecha_nacimiento
                        session['user_address'] = profile.get('direccion', '')
                        session['user_description'] = profile.get('descripcion', '')
                        session['user_area_expertise'] = profile.get('area_expertise', '')
                        session['user_info_adicional'] = profile.get('info_adicional', '')
                        
                        cursor.execute("""
                            UPDATE usuario 
                            SET last_login = %s 
                            WHERE email = %s
                        """, (datetime.now(), form.email.data))
                        conn.commit()
                        
                        login_user(user)
                        flash('Has iniciado sesión exitosamente', 'success')
                        return redirect(url_for('auth.dashboard'))
                else:
                    from werkzeug.security import check_password_hash
                    if check_password_hash(stored_password, form.password.data):
                        cursor.execute("""
                            SELECT p.*, u.email, u.rol 
                            FROM perfil p 
                            JOIN usuario u ON p.usuario_email = u.email 
                            WHERE u.email = %s
                        """, (form.email.data,))
                        profile = cursor.fetchone()
                        
                        if not profile:
                            flash("No se encontraron datos de perfil para el usuario.", "error")
                            return render_template('templatesLogin/login.html', form=form)
                        
                        fecha_nacimiento = profile.get('fecha_nacimiento', '')
                        if fecha_nacimiento:
                            try:
                                fecha_nacimiento = datetime.strptime(str(fecha_nacimiento), "%Y-%m-%d")
                                fecha_nacimiento = fecha_nacimiento.strftime("%d/%m/%Y")
                            except ValueError:
                                fecha_nacimiento = None
                        
                        user = User(user_data)
                        
                        session['user_email'] = user.email
                        session['user_name'] = profile.get('nombre', '')
                        session['user_role'] = profile.get('rol', '')
                        session['user_birthdate'] = fecha_nacimiento
                        session['user_address'] = profile.get('direccion', '')
                        session['user_description'] = profile.get('descripcion', '')
                        session['user_area_expertise'] = profile.get('area_expertise', '')
                        session['user_info_adicional'] = profile.get('info_adicional', '')
                        
                        cursor.execute("""
                            UPDATE usuario 
                            SET last_login = %s 
                            WHERE email = %s
                        """, (datetime.now(), form.email.data))
                        conn.commit()
                        
                        login_user(user)
                        flash('Has iniciado sesión exitosamente', 'success')
                        return redirect(url_for('auth.dashboard'))
            
            flash('Correo electrónico o contraseña inválidos', 'error')
        except mysql.connector.Error as e:
            print(f"Error de base de datos: {e}")
            flash('Error al conectar con la base de datos', 'error')
        except Exception as e:
            print(f"Error en login: {e}")
            flash('Error al intentar iniciar sesión', 'error')
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    return render_template('templatesLogin/login.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM usuario WHERE email = %s", (form.email.data,))
            if cursor.fetchone():
                flash('El email ya está registrado', 'error')
                return render_template('templatesLogin/register.html', form=form)
            
            hashed_password = generate_password_hash(form.password1.data)
            cursor.execute("""
                INSERT INTO usuario (email, password, is_active, is_staff)
                VALUES (%s, %s, %s, %s)
            """, (form.email.data, hashed_password, True, False))
            
            cursor.execute("""
                INSERT INTO perfil (
                    usuario_email, nombre, fecha_nacimiento, direccion,
                    descripcion, area_expertise, info_adicional
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                form.email.data, form.nombre.data, form.fecha_nacimiento.data,
                form.direccion.data, form.descripcion.data,
                form.area_expertise.data, form.informacion_adicional.data
            ))
            
            conn.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login.login'))
            
        except Exception as e:
            print(f"Error en registro: {e}")
            flash('Error al registrar usuario', 'error')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('templatesLogin/register.html', form=form)

@login_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login.login'))
