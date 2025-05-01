# models/solucion.py (versión para Flask)

import requests
import os
from urllib.parse import unquote
from config_flask import MEDIA_ROOT

# -------------------------------
# Clase para peticiones API REST
# -------------------------------
class APIClient:
    BASE_URL = "http://190.217.58.246:5186/api/SGV/procedures/execute"

    def __init__(self, table_name):
        self.table_name = table_name

    def _make_request(self, procedure, where_condition=None, order_by=None, limit_clause=None, json_data=None, select_columns=None):
        payload = {
            "procedure": procedure,
            "parameters": {
                "table_name": self.table_name,
                "where_condition": where_condition,
                "order_by": order_by,
                "limit_clause": limit_clause,
                "json_data": json_data or {},
                "select_columns": select_columns
            }
        }
        try:
            response = requests.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error en _make_request: {e}")
            return None

    def get_data(self, where_condition=None, **kwargs):
        resp = self._make_request("select_json_entity", where_condition=where_condition, **kwargs)
        return resp.get('outputParams', {}).get('result', []) if resp else []

    def insert_data(self, json_data):
        return self._make_request("insert_json_entity", json_data=json_data)

    def delete_data(self, where_condition):
        return self._make_request("delete_json_entity", where_condition=where_condition)

    def update_data(self, where_condition, json_data):
        return self._make_request("update_json_entity", where_condition=where_condition, json_data=json_data)

    def auto_update_data(self, where_condition, json_data):
        current_data = self.get_data(where_condition=where_condition)
        if not current_data:
            return None

        current_data = current_data[0]
        updates = {k: v for k, v in json_data.items() if current_data.get(k) != v}

        return self.update_data(where_condition, updates) if updates else None


# ----------------------------
# APIs auxiliares de catálogos
# ----------------------------
class FocoInnovacionAPI:
    @staticmethod
    def get_focos():
        try:
            resp = requests.get("http://190.217.58.246:5186/api/sgv/foco_innovacion")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error al obtener focos: {e}")
            return []

class TipoInnovacionAPI:
    @staticmethod
    def get_tipo_innovacion():
        try:
            resp = requests.get("http://190.217.58.246:5186/api/sgv/tipo_innovacion")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error al obtener tipos: {e}")
            return []


# ---------------------------------------------
# Relación Solucion - Usuario (simulado en API)
# ---------------------------------------------
class SolucionUsuario:
    @staticmethod
    def get_solucion_by_codigo(codigo_solucion):
        try:
            client = APIClient('solucion')
            data = client.get_data(where_condition=f"codigo_solucion = '{codigo_solucion}'")
            return data[0] if data else None
        except Exception as e:
            print(f"Error obteniendo solucion: {e}")
            return None

    @staticmethod
    def insert_solucion_and_associate_user(form, user_email):
        try:
            focos = FocoInnovacionAPI.get_focos()
            tipos = TipoInnovacionAPI.get_tipo_innovacion()

            foco = next((f for f in focos if f['id'] == form.cleaned_data['id_foco_innovacion']), None)
            tipo = next((t for t in tipos if t['id'] == form.cleaned_data['id_tipo_innovacion']), None)

            if not foco or not tipo:
                return False, "Datos de innovación no encontrados"

            json_data = {
                'titulo': form.cleaned_data['titulo'],
                'descripcion': form.cleaned_data['descripcion'],
                'palabras_claves': form.cleaned_data['palabras_claves'],
                'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                'fecha_creacion': form.cleaned_data['fecha_creacion'],
                'id_foco_innovacion': foco['id'],
                'id_tipo_innovacion': tipo['id'],
                'creador_por': user_email,
                'quien_desarrollo': form.cleaned_data.get('quien_desarrollo'),
                'area_unidad_desarrollo': form.cleaned_data.get('area_unidad_desarrollo')
            }

            client = APIClient('solucion')
            response = client.insert_data(json_data=json_data)

            if response and 'codigo_solucion' in response:
                return True, 'Solución creada y asociada correctamente'
            return False, 'No se pudo registrar la solución'

        except Exception as e:
            return False, f'Error: {e}'


# ---------------------------------------
# Funcionalidad para guardar archivos
# ---------------------------------------
def save_archivo(archivo):
    try:
        filename = archivo.filename
        path = os.path.join(MEDIA_ROOT, filename)
        archivo.save(path)
        return f"/media/{filename}"
    except Exception as e:
        print(f"Error guardando archivo: {e}")
        return None
