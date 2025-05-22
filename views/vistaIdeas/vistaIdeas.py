from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.api_client import APIClient
from config_flask import API_CONFIG
from forms.formsIdeas.formsIdeas import IdeasForm

ideas_bp = Blueprint('ideas', __name__)
api_client = APIClient(API_CONFIG['base_url'])

@ideas_bp.route('/ideas')
def list_ideas():
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para ver las ideas', 'error')
            return redirect(url_for('login.login_view'))
            
        # Obtener filtros de la URL
        tipo_innovacion = request.args.get('tipo_innovacion')
        foco_innovacion = request.args.get('foco_innovacion')
        
        # Obtener datos
        ideas = api_client.get_ideas(tipo_innovacion, foco_innovacion) or []
        tipos = api_client.get_tipos_innovacion() or []
        focos = api_client.get_focos_innovacion() or []
        

        
        return render_template('templatesIdeas/list.html', 
                             ideas=ideas,
                             tipos=tipos,
                             focos=focos)
    except Exception as e:
        flash(f'Error al cargar las ideas: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@ideas_bp.route('/ideas/<int:codigo_idea>')
def view_idea(codigo_idea):
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para ver la idea', 'error')
            return redirect(url_for('login.login_view'))
            
        idea = api_client.get_idea(codigo_idea)
        if not idea:
            flash('Idea no encontrada', 'error')
            ideas = api_client.get_ideas() or []
            return render_template('templatesIdeas/list.html', ideas=ideas)
            
        return render_template('templatesIdeas/view.html', idea=idea)
    except Exception as e:
        flash(f'Error al cargar la idea: {str(e)}', 'error')
        return redirect(url_for('ideas.list_ideas'))

@ideas_bp.route('/ideas/create', methods=['GET', 'POST'])
def create_idea():
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para crear una idea', 'error')
            return redirect(url_for('login.login_view'))
            
        form = IdeasForm()
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_innovacion() or []
        focos = api_client.get_focos_innovacion() or []
        
        # Si no hay tipos o focos, usar valores por defecto
        if not tipos:
            tipos = [{'id': 1, 'nombre': 'Tipo 1'}, {'id': 2, 'nombre': 'Tipo 2'}]
        if not focos:
            focos = [{'id': 1, 'nombre': 'Foco 1'}, {'id': 2, 'nombre': 'Foco 2'}]
            
        form.tipo_innovacion.choices = [(t['id'], t['nombre']) for t in tipos]
        form.foco_innovacion.choices = [(f['id'], f['nombre']) for f in focos]
        
        if form.validate_on_submit():
            idea_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'tipo_innovacion': form.tipo_innovacion.data,
                'foco_innovacion': form.foco_innovacion.data,
                'usuario_email': session.get('user_email')
            }
            
            response = api_client.create_idea(idea_data)
            if response:
                flash('Idea creada exitosamente', 'success')
                return redirect(url_for('ideas.list_ideas'))
            else:
                flash('Error al crear la idea', 'error')
                
        return render_template('templatesIdeas/create.html', form=form)
    except Exception as e:
        flash(f'Error al crear la idea: {str(e)}', 'error')
        return render_template('templatesIdeas/create.html', form=form)

@ideas_bp.route('/ideas/<int:codigo_idea>/edit', methods=['GET', 'POST'])
def update_idea(codigo_idea):
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para editar la idea', 'error')
            return redirect(url_for('login.login_view'))
            
        idea = api_client.get_idea(codigo_idea)
        if not idea:
            flash('Idea no encontrada', 'error')
            return redirect(url_for('ideas.list_ideas'))
            
        form = IdeasForm(obj=idea)
        
        # Cargar opciones para los select
        tipos = api_client.get_tipos_innovacion() or []
        focos = api_client.get_focos_innovacion() or []
        
        # Si no hay tipos o focos, usar valores por defecto
        if not tipos:
            tipos = [{'id': 1, 'nombre': 'Tipo 1'}, {'id': 2, 'nombre': 'Tipo 2'}]
        if not focos:
            focos = [{'id': 1, 'nombre': 'Foco 1'}, {'id': 2, 'nombre': 'Foco 2'}]
            
        form.tipo_innovacion.choices = [(t['id'], t['nombre']) for t in tipos]
        form.foco_innovacion.choices = [(f['id'], f['nombre']) for f in focos]
        
        if form.validate_on_submit():
            idea_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'tipo_innovacion': form.tipo_innovacion.data,
                'foco_innovacion': form.foco_innovacion.data
            }
            
            response = api_client.update_idea(codigo_idea, idea_data)
            if response:
                flash('Idea actualizada exitosamente', 'success')
                return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))
            else:
                flash('Error al actualizar la idea', 'error')
                
        return render_template('templatesIdeas/edit.html', form=form, idea=idea)
    except Exception as e:
        flash(f'Error al actualizar la idea: {str(e)}', 'error')
        return redirect(url_for('ideas.list_ideas'))

@ideas_bp.route('/ideas/<int:codigo_idea>/delete', methods=['POST'])
def delete_idea(codigo_idea):
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para eliminar la idea', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.delete_idea(codigo_idea)
        if response:
            flash('Idea eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la idea', 'error')
            
        return redirect(url_for('ideas.list_ideas'))
    except Exception as e:
        flash(f'Error al eliminar la idea: {str(e)}', 'error')
        return redirect(url_for('ideas.list_ideas'))

@ideas_bp.route('/ideas/<int:codigo_idea>/confirmar', methods=['POST'])
def confirmar_idea(codigo_idea):
    try:
        if not session.get('user_email'):
            flash('Debe iniciar sesión para confirmar la idea', 'error')
            return redirect(url_for('login.login_view'))
            
        response = api_client.confirmar_idea(codigo_idea)
        if response:
            flash('Idea confirmada exitosamente', 'success')
        else:
            flash('Error al confirmar la idea', 'error')
            
        return redirect(url_for('ideas.view_idea', codigo_idea=codigo_idea))
    except Exception as e:
        flash(f'Error al confirmar la idea: {str(e)}', 'error')
        return redirect(url_for('ideas.list_ideas'))

@ideas_bp.route('/ideas/matriz-evaluacion')
def matriz_evaluacion():
    return render_template('templatesIdeas/matriz_evaluacion.html')

@ideas_bp.route('/ideas/estadisticas')
def estadisticas():
    return render_template('templatesIdeas/estadisticas.html')

@ideas_bp.route('/ideas/retos')
def retos():
    return render_template('templatesIdeas/retos.html')

@ideas_bp.route('/ideas/top-generadores')
def top_generadores():
    return render_template('templatesIdeas/top_generadores.html')

@ideas_bp.route('/ideas/evaluacion')
def evaluacion():
    return render_template('templatesIdeas/evaluacion.html')

@ideas_bp.route('/ideas/mercado')
def mercado():
    return render_template('templatesIdeas/mercado.html')