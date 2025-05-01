from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime
from werkzeug.utils import secure_filename
from urllib.parse import unquote
import os, json, requests
# from flask_login import login_required, current_user
import mysql.connector
from config_flask import DATABASE_CONFIG

#from models.api_client import APIClient, FocoInnovacionAPI, TipoInnovacionAPI
#from forms.formsSoluciones import SolucionesForm
#from utils.notificaciones import create_notification
from forms.formsSoluciones.formsSoluciones import SolucionesUpdateForm, SolucionesForm

# Crear un solo blueprint para soluciones
soluciones_bp = Blueprint('soluciones', __name__)

@soluciones_bp.route('/soluciones/listar',methods = ['GET'])
def listar():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login.login'))

    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todas las soluciones
        cursor.execute("""
            SELECT s.*, u.email as creador_email 
            FROM solucion s 
            LEFT JOIN usuario u ON s.creador_por = u.email
        """)
        soluciones = cursor.fetchall()
        
        return render_template('templatesSoluciones/list_soluciones.html', soluciones=soluciones)
        
    except Exception as e:
        flash(f'Error al cargar las soluciones: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
    finally:
        if 'conn' in locals():
            conn.close()

@soluciones_bp.route('/soluciones/crear', methods=['GET', 'POST'])
def create():
    form = SolucionesUpdateForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
            cursor = conn.cursor()
            
            # Aquí iría la lógica para crear una solución
            # Por ahora solo mostramos un mensaje de éxito
            flash('Solución creada exitosamente', 'success')
            return redirect(url_for('soluciones.listar'))
            
        except Exception as e:
            flash(f'Error al crear la solución: {str(e)}', 'danger')
        finally:
            if 'conn' in locals():
                conn.close()
    
    return render_template('templatesSoluciones/create.html', form=form)

@soluciones_bp.route('/soluciones/calendario')
def calendario():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        return render_template('calendar.html')
        
    except Exception as e:
        flash(f'Error al cargar el calendario: {str(e)}', 'danger')
        return redirect(url_for('soluciones.listar'))
    finally:
        if 'conn' in locals():
            conn.close()

@soluciones_bp.route('/soluciones/ultimos-lanzamientos')
def ultimos_lanzamientos():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        return render_template('templatesSoluciones/ultimos_lanzamientos.html')
        
    except Exception as e:
        flash(f'Error al cargar los últimos lanzamientos: {str(e)}', 'danger')
        return redirect(url_for('soluciones.listar'))
    finally:
        if 'conn' in locals():
            conn.close()



@soluciones_bp.route('/soluciones/proximos-lanzamientos')
def proximos_lanzamientos():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        return render_template('templatesSoluciones/proximos_lanzamientos.html')
        
    except Exception as e:
        flash(f'Error al cargar los próximos lanzamientos: {str(e)}', 'danger')
        return redirect(url_for('soluciones.listar'))
    finally:
        if 'conn' in locals():
            conn.close()
