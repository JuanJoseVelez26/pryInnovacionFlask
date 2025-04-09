from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import APIClient  # Asegúrate de que el modelo APIClient esté importado

# Función para cargar la página principal de la aplicación y mostrar notificaciones
def app(request):
    # Obtén el email del usuario desde la sesión
    user_email = request.session.get('user_email')

    # Verificar si el usuario ha iniciado sesión
    if not user_email:
        messages.warning(request, "Debes iniciar sesión para ver tus notificaciones.")
        return redirect('login:login')  # Ajusta el nombre de la ruta según tu sistema

    # Llama a la API para obtener las notificaciones del usuario
    api_client = APIClient(table_name="notificaciones")  # Cambia "notificaciones" al nombre de tu tabla
    where_condition = f"usuario_email = '{user_email}'"  # Filtra las notificaciones por el email del usuario
    notificaciones = api_client.get_data(where_condition=where_condition)

    # Depuración: imprimir las notificaciones en la consola
    print("Notificaciones recuperadas:", notificaciones)

    # Si las notificaciones están vacías o no tienen los campos esperados, genera un mensaje
    if not notificaciones or not isinstance(notificaciones, list):
        messages.warning(request, "No se pudieron cargar las notificaciones.")
        notificaciones = []  # Asegúrate de enviar una lista vacía para evitar errores en la plantilla

    # Ordena las notificaciones por 'leida' (False primero, luego True)
    notificaciones = sorted(notificaciones, key=lambda x: x.get('leida', True))

    # Envía las notificaciones a la plantilla
    return render(request, 'app.html', {'notificaciones': notificaciones})


# Función para marcar una notificación como leída
def marcar_leida(request):
    if request.method == 'POST':
        notificacion_id = request.POST.get('id')  # Obtiene el ID de la notificación desde el formulario
        
        if notificacion_id:
            # Llama a la API para actualizar el estado de la notificación
            api_client = APIClient(table_name="notificaciones")  # Cambia "notificaciones" al nombre correcto de tu tabla
            where_condition = f"id = {notificacion_id}"  # Condición WHERE para identificar la notificación
            json_data = {"leida": True}  # Dato a actualizar
            response = api_client.update_data(where_condition=where_condition, json_data=json_data)
            
            if response:
                messages.success(request, "Notificación marcada como leída.")
            else:
                messages.error(request, "No se pudo marcar como leída. Intenta nuevamente.")
        else:
            messages.error(request, "ID de notificación no válido.")
        
        # Redirige a la página principal después de procesar
        return redirect('/app/')  

# Función para eliminar una notificación
def eliminar_notificacion(request):
    if request.method == 'POST':
        notificacion_id = request.POST.get('id')  # Obtiene el ID de la notificación desde el formulario
        
        if notificacion_id:
            # Llama a la API para eliminar la notificación
            api_client = APIClient(table_name="notificaciones")  # Cambia "notificaciones" al nombre correcto de tu tabla
            where_condition = f"id = {notificacion_id}"  # Condición WHERE para identificar la notificación
            response = api_client.delete_data(where_condition=where_condition)
            
            if response:
                messages.success(request, "Notificación eliminada correctamente.")
            else:
                messages.error(request, "No se pudo eliminar la notificación. Intenta nuevamente.")
        else:
            messages.error(request, "ID de notificación no válido.")
        
        # Redirige a la página principal después de procesar
        return redirect('/app/')  
    



def listar_proyectos(request):
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')
    try:
        # Llamada a la API para obtener los proyectos
        client = APIClient('proyecto')  # Asume que el nombre de la tabla es 'proyecto'
        proyectos = client.get_data()  # Obtienes los proyectos de la API

        # Imprimir los proyectos obtenidos de la API
        print(f"Proyectos obtenidos: {proyectos}")
        
        # Filtrar los proyectos por tipo_origen
        ideas = [p for p in proyectos if p['tipo_origen'] == 'idea']
        oportunidades = [p for p in proyectos if p['tipo_origen'] == 'oportunidad']
        soluciones = [p for p in proyectos if p['tipo_origen'] == 'solución']
        
        # Imprimir los proyectos filtrados por tipo
        print(f"Ideas: {ideas}")
        print(f"Oportunidades: {oportunidades}")
        print(f"Soluciones: {soluciones}")
        
        # Pasar los proyectos filtrados al template
        return render(request, 'listar_proyectos.html', {
            'ideas': ideas,
            'oportunidades': oportunidades,
            'soluciones': soluciones
        })
    except Exception as e:
        print(f"Error al obtener los proyectos: {e}")
        return render(request, 'listar_proyectos.html', {'proyectos': []})



