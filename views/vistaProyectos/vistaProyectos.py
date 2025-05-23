from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from utils.api_client import APIClient
from config_flask import API_CONFIG

proyectos_bp = Blueprint('proyectos', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@proyectos_bp.route('/proyectos')
def list_proyectos():
    try:
        # Verificar si hay sesión activa
        if not session.get('user_email'):
            flash('Debe iniciar sesión para ver los proyectos', 'error')
            return redirect(url_for('login.login_view'))

        # Obtener todas las ideas, oportunidades y soluciones
        try:
            ideas = api_client.get_ideas()
            if not isinstance(ideas, list):
                ideas = []
        except Exception as e:
            print(f'Error al obtener ideas: {str(e)}')
            ideas = []

        try:
            oportunidades = api_client.get_oportunidades()
            if not isinstance(oportunidades, list):
                oportunidades = []
        except Exception as e:
            print(f'Error al obtener oportunidades: {str(e)}')
            oportunidades = []

        try:
            soluciones = api_client.get_soluciones()
            if not isinstance(soluciones, list):
                soluciones = []
        except Exception as e:
            print(f'Error al obtener soluciones: {str(e)}')
            soluciones = []

        # Formatear los datos para la vista
        proyectos = {
            'ideas': [{
                'tipo': 'Idea',
                'titulo': idea.get('titulo', 'Sin título'),
                'descripcion': idea.get('descripcion', 'Sin descripción'),
                'fecha': idea.get('fecha_creacion', ''),
                'estado': idea.get('estado', 'Pendiente'),
                'url': url_for('ideas.list_ideas')
            } for idea in ideas],
            
            'oportunidades': [{
                'tipo': 'Oportunidad',
                'titulo': oportunidad.get('titulo', 'Sin título'),
                'descripcion': oportunidad.get('descripcion', 'Sin descripción'),
                'fecha': oportunidad.get('fecha_creacion', ''),
                'estado': oportunidad.get('estado', 'Pendiente'),
                'url': url_for('oportunidades.list_oportunidades')
            } for oportunidad in oportunidades],
            
            'soluciones': [{
                'tipo': 'Solución',
                'titulo': solucion.get('titulo', 'Sin título'),
                'descripcion': solucion.get('descripcion', 'Sin descripción'),
                'fecha': solucion.get('fecha_creacion', ''),
                'estado': solucion.get('estado', 'Pendiente'),
                'url': url_for('soluciones.list_soluciones')
            } for solucion in soluciones]
        }

        # Combinar todos los proyectos en una sola lista
        todos_proyectos = []
        todos_proyectos.extend(proyectos['ideas'])
        todos_proyectos.extend(proyectos['oportunidades'])
        todos_proyectos.extend(proyectos['soluciones'])

        # Ordenar por fecha de creación (más recientes primero)
        todos_proyectos.sort(key=lambda x: x['fecha'] if x['fecha'] else '', reverse=True)

        return render_template('templatesProyectos/list.html', 
                             proyectos=todos_proyectos,
                             total_ideas=len(proyectos['ideas']),
                             total_oportunidades=len(proyectos['oportunidades']),
                             total_soluciones=len(proyectos['soluciones']))
                             
    except Exception as e:
        print(f'Error general en list_proyectos: {str(e)}')
        flash('Error al cargar los proyectos. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('dashboard.index'))
