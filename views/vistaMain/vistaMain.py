from flask import Blueprint, render_template, session, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Verificar si hay sesión activa
    if not session.get('user_email'):
        return redirect(url_for('login.login_view'))
    return render_template('templatesMain/index.html')