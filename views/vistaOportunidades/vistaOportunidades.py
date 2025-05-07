from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_required, current_user
import psycopg2
from psycopg2.extras import DictCursor
from config_flask import DATABASE_CONFIG

oportunidades_bp = Blueprint('oportunidades', __name__)

@oportunidades_bp.route('/oportunidades/crear', methods=['GET', 'POST'])
# @login_required
def create():
    if request.method == 'POST':
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
            cursor = conn.cursor()
            
            # Aquí iría la lógica para crear una oportunidad
            # Por ahora solo mostramos un mensaje de éxito
            flash('Oportunidad creada exitosamente', 'success')
            return redirect(url_for('oportunidades.create'))
            
        except Exception as e:
            flash(f'Error al crear la oportunidad: {str(e)}', 'danger')
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    return render_template('templatesOportunidades/create.html')

@oportunidades_bp.route('/oportunidades/tabla-fuentes')
# @login_required
def tabla_fuentes():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Aquí iría la lógica para obtener las fuentes
        # Por ahora solo renderizamos la plantilla
        return render_template('templatesOportunidades/tabla_fuentes.html')
        
    except Exception as e:
        flash(f'Error al cargar la tabla de fuentes: {str(e)}', 'danger')
        return redirect(url_for('oportunidades.create'))
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@oportunidades_bp.route('/oportunidades/registro-experto', methods=['GET', 'POST'])
# @login_required
def registro_experto():
    if request.method == 'POST':
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG['postgresql'])
            cursor = conn.cursor()
            
            # Aquí iría la lógica para registrar un experto
            # Por ahora solo mostramos un mensaje de éxito
            flash('Experto registrado exitosamente', 'success')
            return redirect(url_for('oportunidades.registro_experto'))
            
        except Exception as e:
            flash(f'Error al registrar el experto: {str(e)}', 'danger')
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    return render_template('templatesOportunidades/registro_experto.html')
