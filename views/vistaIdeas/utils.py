from datetime import datetime
from .models import APIClient

def create_notification(experto_email, tipo_entidad, entidad_titulo, accion, usuario_email, mensaje_experto=None):
    """
    Crea una notificación en la base de datos.
    
    Args:
        experto_email (str): Email del experto que realiza la acción
        tipo_entidad (str): Tipo de entidad (idea, proyecto, etc.)
        entidad_titulo (str): Título de la entidad
        accion (str): Acción realizada (crear, actualizar, eliminar)
        usuario_email (str): Email del usuario afectado
        mensaje_experto (str, optional): Mensaje adicional del experto
    """
    data = {
        'experto_email': experto_email,
        'tipo_entidad': tipo_entidad,
        'entidad_titulo': entidad_titulo,
        'accion': accion,
        'usuario_email': usuario_email,
        'mensaje_experto': mensaje_experto,
        'fecha_creacion': datetime.utcnow().isoformat()
    }
    
    try:
        APIClient('notificacion').insert_data(json_data=data)
    except Exception as e:
        print(f"Error al crear notificación: {e}") 