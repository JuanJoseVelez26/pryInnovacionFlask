import requests
from config_flask import API_CONFIG
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.headers = API_CONFIG['headers']
        self.session = requests.Session()
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """Realiza una petición HTTP al API.
        
        Args:
            method (str): Método HTTP (GET, POST, PUT, DELETE)
            endpoint (str): Endpoint de la API
            data (dict, optional): Datos para el cuerpo de la petición
            params (dict, optional): Parámetros de consulta
            
        Returns:
            dict: Respuesta del API en formato JSON o None si hay error
        """
        url = f'{self.base_url}/{endpoint}'
        headers = self.headers
        
        print(f'[API] Realizando petición {method} a {url}')
        print(f'[API] Datos: {data}')
        print(f'[API] Parámetros: {params}')
        print(f'[API] Headers: {headers}')
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            print(f'[API] Status Code: {response.status_code}')
            print(f'[API] Response Headers: {dict(response.headers)}')
            
            if response.status_code == 404:
                print(f'[API] Endpoint no encontrado: {endpoint}')
                return None
            elif response.status_code == 401:
                print(f'[API] No autorizado')
                return None
            elif response.status_code == 500:
                print(f'[API] Error interno del servidor')
                return None
            
            if response.text:
                return response.json()
            return None
            
        except requests.exceptions.RequestException as e:
            print(f'[API] Error de conexión: {str(e)}')
            return None
            

    # Métodos para autenticación
    def login(self, email, password):
        """Autentica un usuario con email y contraseña

        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario

        Returns:
            dict: Datos del usuario o None si hay error
        """
        data = {
            'userField': 'email',
            'passwordField': 'password',
            'userValue': email,
            'passwordValue': password
        }
        response = self._make_request('POST', 'InnovacionUSB/usuario/verificar-contrasena', data=data)
        print(f'[API] Respuesta del login: {response}')
        return response
        
    def register(self, user_data):
        """Registra un nuevo usuario"""
        return self._make_request('POST', 'auth/register', user_data)
        
    def get_user_profile(self, user_id):
        """Obtiene el perfil de un usuario"""
        return self._make_request('GET', f'users/{user_id}/profile')

    def update_user_profile(self, user_id, profile_data):
        """Actualiza el perfil de un usuario"""
        return self._make_request('PUT', f'users/{user_id}/profile', profile_data)

    def change_password(self, user_id, password_data):
        """Cambia la contraseña de un usuario"""
        return self._make_request('POST', f'users/{user_id}/change-password', password_data)

    # Métodos para procedimientos
    def get_procedures(self, where_condition=None, order_by=None, limit=None, select_columns=None):
        """Obtiene procedimientos"""
        params = {
            'where': where_condition,
            'orderBy': order_by,
            'limit': limit,
            'select': select_columns
        }
        return self._make_request('GET', '/SGV/procedures/execute', params=params)
        
    def get_procedures(self):
        """Get all procedures"""
        return self._make_request('GET', 'procedures')

    def get_ideas(self):
        """Get all ideas"""
        return self._make_request('GET', '/api/InnovacionUSB/Idea')

    def get_oportunidades(self):
        """Get all opportunities"""
        return self._make_request('GET', '/api/innovacionusb/oportunidad')

    def get_soluciones(self):
        """Get all solutions"""
        return self._make_request('GET', '/api/innovacionusb/solucion')

    def create_procedure(self, data):
        """Crea un nuevo procedimiento"""
        return self._make_request('POST', '/SGV/procedures/execute', data=data)
        
    def update_procedure(self, where_condition, data):
        """Actualiza un procedimiento"""
        if not where_condition or not data:
            logger.error("Faltan datos: where_condition o data son necesarios.")
            return None
            
        request_data = {
            'where': where_condition,
            'data': data
        }
        return self._make_request('PUT', '/SGV/procedures/execute', data=request_data)
        
    def delete_procedure(self, where_condition):
        """Elimina un procedimiento"""
        if not where_condition:
            logger.error("Falta la condición WHERE para eliminar.")
            return None
            
        params = {'where': where_condition}
        return self._make_request('DELETE', '/SGV/procedures/execute', params=params)

    # Métodos para ideas
    def get_ideas(self, tipo_innovacion=None, foco_innovacion=None):
        """Obtiene la lista de ideas

        Args:
            tipo_innovacion (str, optional): Filtrar por tipo de innovación
            foco_innovacion (str, optional): Filtrar por foco de innovación

        Returns:
            list: Lista de ideas
        """
        try:
            params = {}
            if tipo_innovacion:
                params['id_tipo_innovacion'] = tipo_innovacion
            if foco_innovacion:
                params['id_foco_innovacion'] = foco_innovacion
                
            response = self._make_request('GET', 'InnovacionUSB/Idea', params=params)
            return response
        except Exception as e:
            print(f"[API] Error al obtener ideas: {str(e)}")
            return []

    def get_idea(self, codigo_idea):
        try:
            response = self._make_request('GET', f'InnovacionUSB/Idea/{codigo_idea}')
            return response
        except Exception as e:
            print(f"[API] Error al obtener idea: {str(e)}")
            return None

    def create_idea(self, idea_data):
        try:
            # Asegurar que los campos coincidan con el esquema de la BD
            data = {
                'id_tipo_innovacion': idea_data.get('tipo_innovacion'),
                'id_foco_innovacion': idea_data.get('foco_innovacion'),
                'titulo': idea_data.get('titulo'),
                'descripcion': idea_data.get('descripcion'),
                'fecha_creacion': idea_data.get('fecha_creacion', datetime.now().strftime('%Y-%m-%d')),
                'palabras_claves': idea_data.get('palabras_claves'),
                'recursos_requeridos': idea_data.get('recursos_requeridos'),
                'archivo_multimedia': idea_data.get('archivo_multimedia', ''),
                'creador_por': idea_data.get('usuario_email'),
                'estado': False
            }
            response = self._make_request('POST', 'InnovacionUSB/Idea', data=data)
            return response
        except Exception as e:
            print(f"[API] Error al crear idea: {str(e)}")
            return None

    def update_idea(self, codigo_idea, idea_data):
        try:
            # Asegurar que los campos coincidan con el esquema de la BD
            data = {
                'id_tipo_innovacion': idea_data.get('tipo_innovacion'),
                'id_foco_innovacion': idea_data.get('foco_innovacion'),
                'titulo': idea_data.get('titulo'),
                'descripcion': idea_data.get('descripcion'),
                'palabras_claves': idea_data.get('palabras_claves'),
                'recursos_requeridos': idea_data.get('recursos_requeridos'),
                'archivo_multimedia': idea_data.get('archivo_multimedia', '')
            }
            response = self._make_request('PUT', f'InnovacionUSB/Idea/{codigo_idea}', data=data)
            return response
        except Exception as e:
            print(f"[API] Error al actualizar idea: {str(e)}")
            return None

    def delete_idea(self, codigo_idea):
        try:
            response = self._make_request('DELETE', f'InnovacionUSB/Idea/{codigo_idea}')
            return response
        except Exception as e:
            print(f"[API] Error al eliminar idea: {str(e)}")
            return None

    def confirmar_idea(self, codigo_idea):
        return self._make_request('POST', f'InnovacionUSB/Idea/Confirmar/{codigo_idea}')

    # Métodos para oportunidades
    def get_oportunidades(self, tipo_innovacion=None, foco_innovacion=None):
        """Obtiene la lista de oportunidades

        Args:
            tipo_innovacion (str, optional): Filtrar por tipo de innovación
            foco_innovacion (str, optional): Filtrar por foco de innovación

        Returns:
            list: Lista de oportunidades
        """
        params = {}
        if tipo_innovacion:
            params['tipo_innovacion'] = tipo_innovacion
        if foco_innovacion:
            params['foco_innovacion'] = foco_innovacion
            
        return self._make_request('GET', 'innovacionusb/oportunidad', params=params)

    def get_oportunidad(self, oportunidad_id):
        return self._make_request('GET', f'innovacionusb/oportunidad/obtener/{oportunidad_id}')

    def create_oportunidad(self, oportunidad_data):
        return self._make_request('POST', 'innovacionusb/oportunidad/crear', oportunidad_data)

    def update_oportunidad(self, oportunidad_id, oportunidad_data):
        return self._make_request('PUT', f'innovacionusb/oportunidad/actualizar/{oportunidad_id}', oportunidad_data)

    def delete_oportunidad(self, oportunidad_id):
        return self._make_request('DELETE', f'innovacionusb/oportunidad/eliminar/{oportunidad_id}')

    def confirmar_oportunidad(self, oportunidad_id):
        return self._make_request('POST', f'innovacionusb/oportunidad/confirmar/{oportunidad_id}')

    # Métodos para soluciones
    def get_soluciones(self, tipo_innovacion=None, foco_innovacion=None):
        """Obtiene la lista de soluciones

        Args:
            tipo_innovacion (str, optional): Filtrar por tipo de innovación
            foco_innovacion (str, optional): Filtrar por foco de innovación

        Returns:
            list: Lista de soluciones
        """
        params = {}
        if tipo_innovacion:
            params['tipo_innovacion'] = tipo_innovacion
        if foco_innovacion:
            params['foco_innovacion'] = foco_innovacion
            
        return self._make_request('GET', 'innovacionusb/solucion', params=params)

    def get_solucion(self, solucion_id):
        return self._make_request('GET', f'innovacionusb/solucion/obtener/{solucion_id}')

    def create_solucion(self, solucion_data):
        return self._make_request('POST', 'innovacionusb/solucion/crear', solucion_data)

    def update_solucion(self, solucion_id, solucion_data):
        return self._make_request('PUT', f'innovacionusb/solucion/actualizar/{solucion_id}', solucion_data)

    def delete_solucion(self, solucion_id):
        return self._make_request('DELETE', f'InnovacionUSB/Solucion/Eliminar/{solucion_id}')

    def confirmar_solucion(self, solucion_id):
        return self._make_request('POST', f'InnovacionUSB/Solucion/Confirmar/{solucion_id}')

    # Métodos para tipos y focos de innovación
    def get_tipos_innovacion(self):
        try:
            response = self._make_request('GET', 'InnovacionUSB/TipoInnovacion')
            if response:
                return response
            return [
                {'id_tipo_innovacion': 1, 'name': 'Tipo 1'},
                {'id_tipo_innovacion': 2, 'name': 'Tipo 2'}
            ]
        except Exception as e:
            print(f"[API] Error al obtener tipos de innovación: {str(e)}")
            return [
                {'id_tipo_innovacion': 1, 'name': 'Tipo 1'},
                {'id_tipo_innovacion': 2, 'name': 'Tipo 2'}
            ]

    def get_focos_innovacion(self):
        try:
            response = self._make_request('GET', 'InnovacionUSB/FocoInnovacion')
            if response:
                return response
            return [
                {'id_foco_innovacion': 1, 'name': 'Foco 1'},
                {'id_foco_innovacion': 2, 'name': 'Foco 2'}
            ]
        except Exception as e:
            print(f"[API] Error al obtener focos de innovación: {str(e)}")
            return [
                {'id_foco_innovacion': 1, 'name': 'Foco 1'},
                {'id_foco_innovacion': 2, 'name': 'Foco 2'}
            ]
        
    def get_tipos_mercado(self):
        """Obtiene los tipos de mercado disponibles."""
        try:
            response = self._make_request('GET', 'innovacionusb/tipo-mercado')
            if response:
                return response
            return [
                {'id': 1, 'nombre': 'Local'},
                {'id': 2, 'nombre': 'Regional'},
                {'id': 3, 'nombre': 'Nacional'},
                {'id': 4, 'nombre': 'Internacional'}
            ]
        except Exception as e:
            print(f"[API] Error al obtener tipos de mercado: {str(e)}")
            return [
                {'id': 1, 'nombre': 'Local'},
                {'id': 2, 'nombre': 'Regional'},
                {'id': 3, 'nombre': 'Nacional'},
                {'id': 4, 'nombre': 'Internacional'}
            ]

    def get_estados(self):
        """Obtiene los estados disponibles para las oportunidades."""
        try:
            response = self._make_request('GET', 'innovacionusb/estado-oportunidad')
            if response:
                return response
            return [
                {'id': 1, 'nombre': 'En Revisión'},
                {'id': 2, 'nombre': 'Aprobada'},
                {'id': 3, 'nombre': 'Rechazada'},
                {'id': 4, 'nombre': 'Confirmada'}
            ]
        except Exception as e:
            print(f"[API] Error al obtener estados: {str(e)}")
            return [
                {'id': 1, 'nombre': 'En Revisión'},
                {'id': 2, 'nombre': 'Aprobada'},
                {'id': 3, 'nombre': 'Rechazada'},
                {'id': 4, 'nombre': 'Confirmada'}
            ]

    def get_user_info(self, email):
        """Obtiene la información del usuario desde el API."""
        try:
            response = self._make_request('GET', f'innovacionusb/usuario/{email}')
            return response
        except Exception as e:
            print(f"[API] Error al obtener información del usuario: {str(e)}")
            return None