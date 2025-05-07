# app/services.py

import os
import requests
from flask import current_app, flash, redirect, url_for, request, session
from werkzeug.utils import secure_filename


# ---- APIs externas de catálogo ----

class FocoInnovacionAPI:
    @staticmethod
    def get_focos():
        url = "http://190.217.58.246:5186/api/sgv/foco_innovacion"
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error al obtener focos: {e}")
            return []


class TipoInnovacionAPI:
    @staticmethod
    def get_tipo_innovacion():
        url = "http://190.217.58.246:5186/api/sgv/tipo_innovacion"
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error al obtener tipos de innovación: {e}")
            return []


# ---- Cliente genérico para procedimientos ----

class APIClient:
    BASE_URL = "http://190.217.58.246:5186/api/SGV/procedures/execute"

    def __init__(self, table_name):
        self.table_name = table_name

    def _request(self, procedure, where=None, order_by=None,
                 limit=None, json_data=None, select_columns=None):
        payload = {
            "procedure": procedure,
            "parameters": {
                "table_name": self.table_name,
                "where_condition": where,
                "order_by": order_by,
                "limit_clause": limit,
                "json_data": json_data or {},
                "select_columns": select_columns,
            }
        }
        try:
            r = requests.post(self.BASE_URL, json=payload)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as err:
            current_app.logger.error(f"HTTP error ({procedure}): {err} / {r.text}")
        except Exception as e:
            current_app.logger.error(f"Error inesperado ({procedure}): {e}")
        return None

    def get_data(self, where=None, **kwargs):
        resp = self._request("select_json_entity", where=where, **kwargs)
        return resp.get("outputParams", {}).get("result", []) if resp else []

    def insert_data(self, json_data):
        return self._request("insert_json_entity", json_data=json_data)

    def update_data(self, where, json_data):
        return self._request("update_json_entity", where=where, json_data=json_data)

    def delete_data(self, where):
        return self._request("delete_json_entity", where=where)

    def auto_update_data(self, where, json_data):
        if not where or not json_data:
            return None
        current = self.get_data(where=where)
        if not current:
            return None
        current = current[0]
        diffs = {k: v for k, v in json_data.items() if current.get(k) != v}
        if diffs:
            return self.update_data(where, diffs)
        else:
            current_app.logger.debug("No hubo cambios en los datos.")
            return None


# ---- Relación Idea ↔ Usuario ----

class IdeaUsuario:
    @staticmethod
    def get_idea_by_codigo(codigo):
        client = APIClient('idea')
        lista = client.get_data(where=f"codigo_idea = '{codigo}'")
        return lista[0] if lista else None

    @staticmethod
    def insert_idea_and_associate_user(form, user_email, archivo=None):
        # Obtener catálogos
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()

        # Buscar en catálogos
        foco = next((f for f in focos if f['id'] == form.id_foco_innovacion.data), None)
        tipo = next((t for t in tipos if t['id'] == form.id_tipo_innovacion.data), None)
        if not foco or not tipo:
            return False, "Foco o Tipo de Innovación inválido."

        # Montar payload
        data = {
            'titulo': form.titulo.data,
            'descripcion': form.descripcion.data,
            'palabras_claves': form.palabras_claves.data,
            'recursos_requeridos': form.recursos_requeridos.data,
            'fecha_creacion': form.fecha_creacion.data.isoformat(),
            'id_foco_innovacion': foco['id'],
            'id_tipo_innovacion': tipo['id'],
            'creador_por': user_email
        }

        # Si hay archivo, lo guardo y guardo su nombre
        if archivo:
            nombre = secure_filename(archivo.filename)
            carpeta = current_app.config['UPLOAD_FOLDER']
            os.makedirs(carpeta, exist_ok=True)
            path = os.path.join(carpeta, nombre)
            archivo.save(path)
            data['archivo_multimedia'] = nombre

        client = APIClient('idea')
        resp = client.insert_data(json_data=data)
        if not resp or 'codigo_idea' not in resp:
            return False, "Error al insertar la idea."

        # Asocio usuario ↔ idea
        codigo = resp['codigo_idea']
        assoc = APIClient('idea_usuario').insert_data(
            json_data={'email_usuario': user_email, 'codigo_idea': codigo}
        )
        if not assoc:
            current_app.logger.warning("Idea creada pero no se pudo asociar al usuario.")
        return True, "Idea creada y asociada con éxito."


# ---- Helpers de vista ----

def save_archivo(file_storage):
    """
    Guarda un FileStorage (werkzeug) en UPLOAD_FOLDER y devuelve el nombre de archivo.
    """
    nombre = secure_filename(file_storage.filename)
    carpeta = current_app.config['UPLOAD_FOLDER']
    os.makedirs(carpeta, exist_ok=True)
    destino = os.path.join(carpeta, nombre)
    file_storage.save(destino)
    return nombre


def crear_idea_y_asociar_usuario(form):
    """
    Lógica de vista para crear idea + asociación, usando `flash` y `redirect`.
    Asume que `session['user_email']` ya está definido.
    """
    user_email = session.get('user_email')
    if not user_email:
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for('auth.login'))

    if not form.validate_on_submit():
        flash("Formulario inválido.", "danger")
        return redirect(url_for('ideas.create_idea'))

    archivo = request.files.get('archivo_multimedia')
    ok, msg = IdeaUsuario.insert_idea_and_associate_user(form, user_email, archivo)
    flash(msg, "success" if ok else "danger")
    if ok:
        return redirect(url_for('ideas.list_ideas'))
    else:
        return redirect(url_for('ideas.create_idea'))
