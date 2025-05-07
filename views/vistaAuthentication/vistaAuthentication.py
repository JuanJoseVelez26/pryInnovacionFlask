from flask import Blueprint, render_template, request, redirect, url_for, session, flash
# from flask_login import login_required, current_user
import psycopg2
from config_flask import DATABASE_CONFIG
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/dashboard')
# @login_required
def dashboard():
    print("--- Entrando a la ruta /dashboard ---") # DEBUG
    conn = None # Inicializar conn a None
    cursor = None # Inicializar cursor a None
    try:
        print("--- Intentando conectar a la BD ---") # DEBUG
        conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
        print("--- Conexión a BD exitosa ---") # DEBUG
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print("--- Cursor creado ---") # DEBUG

        # Obtener estadísticas del usuario
        print("--- Ejecutando query de estadísticas ---") # DEBUG
        cursor.execute("""
            SELECT
                COUNT(*) as total_ideas,
                SUM(CASE WHEN estado = true THEN 1 ELSE 0 END) as ideas_aprobadas,
                SUM(CASE WHEN estado = false THEN 1 ELSE 0 END) as ideas_pendientes
            FROM idea
            WHERE usuario_email = %s
        """, ('usuario@ejemplo.com',))  # Email temporal
        stats = cursor.fetchone()
        print(f"--- Estadísticas obtenidas: {stats} ---") # DEBUG

        # Obtener ideas recientes
        print("--- Ejecutando query de ideas recientes ---") # DEBUG
        cursor.execute("""
            SELECT i.*, ti.nombre as tipo_innovacion_nombre, fi.nombre as foco_innovacion_nombre
            FROM idea i
            LEFT JOIN tipo_innovacion ti ON i.id_tipo_innovacion = ti.id_tipo_innovacion
            LEFT JOIN foco_innovacion fi ON i.id_foco_innovacion = fi.id_foco_innovacion
            WHERE i.usuario_email = %s
            ORDER BY i.fecha_creacion DESC
            LIMIT 5
        """, ('usuario@ejemplo.com',))  # Email temporal
        ideas = cursor.fetchall()
        print(f"--- Ideas obtenidas: {len(ideas)} ideas ---") # DEBUG

        # Formatear fechas
        print("--- Formateando fechas ---") # DEBUG
        for idea in dict(ideas):
            if idea['fecha_creacion']:
                idea['fecha_creacion'] = idea['fecha_creacion'].strftime('%d/%m/%Y')
        print("--- Fechas formateadas ---") # DEBUG

        print("--- Renderizando plantilla dashboard.html ---") # DEBUG
        return render_template('templatesAuthentication/dashboard.html',
                            stats=dict(stats),
                            ideas=ideas)

    except psycopg2.Error as err:
        print(f"!!! Error de PostgreSQL: {err} !!!") # DEBUG
        flash(f'Error de base de datos al cargar el dashboard: {err}', 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        print(f"!!! Error inesperado: {e} !!!") # DEBUG
        flash(f'Error inesperado al cargar el dashboard: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
    finally:
        print("--- Bloque finally del dashboard ---") # DEBUG
        if cursor:
            print("--- Cerrando cursor ---") # DEBUG
            cursor.close()
        if conn:
            print("--- Cerrando conexión BD ---") # DEBUG
            conn.close()

@auth_bp.route('/notificaciones')
# @login_required
def notificaciones():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT *
            FROM notificacion
            WHERE usuario_email = %s
            ORDER BY fecha_creacion DESC
        """, ('usuario@ejemplo.com',))  # Email temporal
        notificaciones = cursor.fetchall()
        
        # Marcar notificaciones como leídas
        cursor.execute("""
            UPDATE notificacion
            SET leida = TRUE
            WHERE usuario_email = %s AND leida = FALSE
        """, ('usuario@ejemplo.com',))  # Email temporal
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return render_template('templatesAuthentication/notificaciones.html',
                             notificaciones=notificaciones)
    except Exception as e:
        flash(f'Error al cargar las notificaciones: {str(e)}', 'danger')
        return redirect(url_for('auth.dashboard'))

@auth_bp.route('/configuracion', methods=['GET', 'POST'])
# @login_required
def configuracion():
    if request.method == 'POST':
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuario
                SET notificaciones_email = %s,
                    notificaciones_push = %s
                WHERE email = %s
            """, (
                'email' in request.form,
                'push' in request.form,
                'usuario@ejemplo.com'  # Email temporal
            ))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Configuración actualizada exitosamente', 'success')
            return redirect(url_for('auth.configuracion'))
        except Exception as e:
            flash(f'Error al actualizar la configuración: {str(e)}', 'danger')
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT notificaciones_email, notificaciones_push
            FROM usuario
            WHERE email = %s
        """, ('usuario@ejemplo.com',))  # Email temporal
        configuracion = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return render_template('templatesAuthentication/configuracion.html',
                             configuracion=configuracion)
    except Exception as e:
        flash(f'Error al cargar la configuración: {str(e)}', 'danger')
        return redirect(url_for('auth.dashboard'))
