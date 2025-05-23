from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from soluciones.models import APIClient, SolucionUsuario, TipoInnovacionAPI, FocoInnovacionAPI
import requests
import json
from django.shortcuts import render, get_object_or_404  
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from soluciones.forms.Soluciones_Form import SolucionesForm
from soluciones.forms.soluciones_update_form import SolucionesUpdateForm
import os
from datetime import datetime
from urllib.parse import unquote
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def list_soluciones(request):
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')

    # Crear instancia de APIClient para la tabla 'solucion'
    client = APIClient('solucion')
    
    # Obtener tipos de innovación y focos de innovación usando las clases de API específicas
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Obtener los valores de los filtros
    selected_tipo = request.GET.get('tipo_innovacion', '')
    selected_foco = request.GET.get('foco_innovacion', '')
    selected_estado = request.GET.get('estado', '')  # Recoger filtro de estado

    # Crear una lista de condiciones WHERE para filtrar las soluciones
    where_condition = []

    if selected_tipo:
        where_condition.append(f"id_tipo_innovacion = {selected_tipo}")
    if selected_foco:
        where_condition.append(f"id_foco_innovacion = {selected_foco}")
    if selected_estado != '':
        if selected_estado == 'True':
            where_condition.append("estado = TRUE")
        elif selected_estado == 'False':
            where_condition.append("estado = FALSE")

    where_condition = " AND ".join(where_condition) if where_condition else ""

    try:
        # Obtener las soluciones desde la API con los filtros
        soluciones = client.get_data(where_condition=where_condition)

        # Crear diccionarios para obtener nombres por ID rápidamente
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        for solucion in soluciones:
            solucion['tipo_innovacion_nombre'] = tipos_dict.get(solucion.get('id_tipo_innovacion'), 'Desconocido')
            solucion['foco_innovacion_nombre'] = focos_dict.get(solucion.get('id_foco_innovacion'), 'Desconocido')

            # Formatear la fecha de creación
            fecha_creacion = solucion.get('fecha_creacion')
            if fecha_creacion:
                try:
                    solucion['fecha_creacion'] = datetime.strptime(fecha_creacion, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                except ValueError:
                    solucion['fecha_creacion'] = "Fecha inválida"

        if not soluciones:
            messages.info(request, 'No hay soluciones disponibles.')
        else:
            messages.info(request, f'Se obtuvieron {len(soluciones)} soluciones.')

    except Exception as e:
        messages.error(request, f'Error al obtener las soluciones: {e}')
        soluciones = []

    # Verificar el rol del usuario logueado
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil_data and perfil_data[0].get('rol', '').lower() == 'experto'

    context = {
        'soluciones': soluciones,
        'tipos': tipos,
        'focos': focos,
        'selected_tipo': selected_tipo,
        'selected_foco': selected_foco,
        'selected_estado': selected_estado,
        'user_email': user_email,
        'is_experto': is_experto,
    }

    return render(request, 'soluciones/list_soluciones.html', context)




# Función para insertar la relación entre el usuario y la solución
def insertar_solucion_usuario(user_email, solucion_codigo):
    try:
        # Crear la relación entre la solución y el usuario
        SolucionUsuario.objects.create(email_usuario=user_email, codigo_solucion=solucion_codigo)
        print(f"Relación creada con éxito: Usuario {user_email} - Solución {solucion_codigo}")
    except Exception as e:
        print(f"Error al insertar la relación: {e}")




def create_solucion(request):
    print("Iniciando la vista create_solucion")
    
    # Verificar si el usuario ha iniciado sesión
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para crear una solución.')
        return redirect('login')
    
    messages.info(request, f'Usuario logueado: {user_email}')
    print(f'Usuario logueado: {user_email}')  # Depuración adicional

    # Inicializar las variables de focos y tipos de innovación
    focos_innovacion = []
    tipos_innovacion = []

    # Obtener dinámicamente los valores de foco_innovacion y tipo_innovacion desde las APIs
    try:
        print("Llamando a la API de foco de innovación...")
        client = APIClient('foco_innovacion')
        focos_innovacion = client.get_data()
        print("Focos de innovación recibidos:", focos_innovacion)

        if 'result' in focos_innovacion:
            try:
                focos_innovacion = json.loads(focos_innovacion['result'][0]['result'])
                print("Focos de innovación decodificados:", focos_innovacion)
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los focos de innovación: {e}')
                print(f'Error al decodificar los focos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron focos de innovación en la respuesta de la API.')
        
        print("Llamando a la API de tipo de innovación...")
        client = APIClient('tipo_innovacion')
        tipos_innovacion = client.get_data()
        print("Tipos de innovación recibidos:", tipos_innovacion)

        if 'result' in tipos_innovacion:
            try:
                tipos_innovacion = json.loads(tipos_innovacion['result'][0]['result'])
                print("Tipos de innovación decodificados:", tipos_innovacion)
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los tipos de innovación: {e}')
                print(f'Error al decodificar los tipos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron tipos de innovación en la respuesta de la API.')

        if not focos_innovacion or not tipos_innovacion:
            messages.info(request, 'No hay focos o tipos de innovación disponibles.')
            print("No hay focos o tipos de innovación disponibles.")
    except Exception as e:
        messages.error(request, f'Error al obtener los datos: {e}')
        print(f'Error al obtener los datos: {e}')
    
    # Asegurarse de que el formulario se inicialice
    if request.method == 'POST':
        form = SolucionesForm(request.POST, request.FILES)
        
        # Mostrar los datos del formulario recibido
        messages.info(request, f'Formulario recibido: {request.POST}')
        print(f'Formulario recibido: {request.POST}')  # Depuración adicional

        if form.is_valid():
            print("Formulario válido")
            print(form.cleaned_data)  # Muestra los datos validados
            messages.info(request, f'Formulario válido, procesando datos...')

            try:
                foco_innovacion_name = int(form.cleaned_data['id_foco_innovacion'])
                tipo_innovacion_name = int(form.cleaned_data['id_tipo_innovacion'])
            except ValueError as e:
                messages.error(request, f'Error al convertir los valores a enteros: {e}')
                print(f'Error al convertir los valores a enteros: {e}')
                return redirect('soluciones:create')

            try:
                foco_innovacion = next((foco for foco in focos_innovacion if foco['id_foco_innovacion'] == foco_innovacion_name), None)
                tipo_innovacion = next((tipo for tipo in tipos_innovacion if tipo['id_tipo_innovacion'] == tipo_innovacion_name), None)

                if foco_innovacion is None:
                    messages.error(request, f'Foco de innovación con ID "{foco_innovacion_name}" no encontrado.')
                    print(f'Foco de innovación con ID "{foco_innovacion_name}" no encontrado.')

                if tipo_innovacion is None:
                    messages.error(request, f'Tipo de innovación con ID "{tipo_innovacion_name}" no encontrado.')
                    print(f'Tipo de innovación con ID "{tipo_innovacion_name}" no encontrado.')

                if foco_innovacion and tipo_innovacion:
                    messages.info(request, f'Foco de Innovación encontrado: {foco_innovacion}, Tipo de Innovación encontrado: {tipo_innovacion}')
                    print(f'Foco de Innovación encontrado: {foco_innovacion}, Tipo de Innovación encontrado: {tipo_innovacion}')

            except Exception as e:
                messages.error(request, f'Error al obtener Foco de Innovación o Tipo de Innovación: {e}')
                print(f'Error al obtener Foco de Innovación o Tipo de Innovación: {e}')
                return redirect('soluciones:create')
            
            client = APIClient('solucion')

            json_data = {
                'titulo': form.cleaned_data['titulo'],
                'descripcion': form.cleaned_data['descripcion'],
                'fecha_creacion': form.cleaned_data['fecha_creacion'].isoformat(),
                'id_foco_innovacion': foco_innovacion['id_foco_innovacion'] if foco_innovacion else None,
                'id_tipo_innovacion': tipo_innovacion['id_tipo_innovacion'] if tipo_innovacion else None,
                'creador_por': user_email,
                'palabras_claves': form.cleaned_data.get('palabras_claves', ''),
                'recursos_requeridos': form.cleaned_data.get('recursos_requeridos', 0),
                'desarrollador_por': form.cleaned_data.get('desarrollador_por', ''),
                'area_unidad_desarrollo': form.cleaned_data.get('area_unidad_desarrollo', '')
            }

            messages.info(request, f'Datos preparados para la API: {json_data}')
            print(f'Datos preparados para la API: {json_data}')  # Depuración adicional

            if 'archivo_multimedia' in request.FILES:
                file = request.FILES['archivo_multimedia']
                try:
                    file_name = default_storage.save(file.name, ContentFile(file.read()))
                    file_url = default_storage.url(file_name)
                    json_data['archivo_multimedia'] = file_url
                    messages.info(request, f'Archivo multimedia cargado con éxito: {file.name}')
                    print(f'Archivo multimedia cargado con éxito: {file.name}')  # Depuración adicional
                except Exception as e:
                    messages.error(request, f'Error al leer el archivo multimedia: {e}')
                    print(f'Error al leer el archivo multimedia: {e}')
                    return redirect('soluciones:create')

            try:
                messages.info(request, f'Enviando datos a la API: {json_data}')
                print(f'Enviando datos a la API: {json_data}')  # Depuración adicional
                response = client.insert_data(json_data=json_data)
                
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                        messages.info(request, f'Respuesta decodificada: {response}')
                        print("Respuesta de la API:", response)
                    except json.JSONDecodeError as e:
                        messages.error(request, f'Error al decodificar la respuesta de la API: {e}')
                        print(f'Error al decodificar la respuesta de la API: {e}')
                        return redirect('soluciones:create')

                messages.info(request, f'Respuesta de la API: {response}')
                print(f'Respuesta de la API: {response}')

                if 'outputParams' in response and response['outputParams'].get('mensaje') == "Inserción realizada correctamente.":
                    messages.success(request, '¡Solución creada con éxito!')
                    print('¡Solución creada con éxito!')
                    return redirect('soluciones:list_soluciones')
                else:
                    messages.error(request, f'Error al crear la solución: {response.get("message", "No se recibió mensaje de error.")}')
                    print(f'Error al crear la solución: {response.get("message", "No se recibió mensaje de error.")}')
            except Exception as e:
                messages.error(request, f'Error al enviar los datos a la API: {e}')
                print(f'Error al enviar los datos a la API: {e}')
        else:
            messages.error(request, 'Formulario inválido, revisa los datos ingresados.')
            print(f'Formulario inválido: {form.errors}')
            return redirect('soluciones:create')

    # Si el método es GET o si el formulario no es válido, inicializar el formulario vacío
    form = SolucionesForm()

    # Retornar el formulario y los datos de las APIs al contexto
    return render(request, 'soluciones/create.html', {'form': form, 'focos_innovacion': focos_innovacion, 'tipos_innovacion': tipos_innovacion})



def delete_solucion(request, codigo_solucion):
    # Verifica si el usuario está autenticado
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para eliminar una solución.')
        return redirect('login:login')

    # Instancia del cliente API
    client = APIClient('solucion')

    # Obtener la solución de la API
    solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")
    
    if not solucion:
        messages.error(request, 'Solución no encontrada.')
        return redirect('soluciones:list_soluciones')

    solucion_data = solucion[0]  # Suponemos que `solucion` es una lista con un solo elemento

    # Obtener los focos y tipos de innovación desde las APIs correspondientes
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Crear diccionarios para obtener los nombres por ID
    focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
    tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

    # Añadir nombres de tipo y foco a la solución
    solucion_data['tipo_innovacion_nombre'] = tipos_dict.get(solucion_data['id_tipo_innovacion'], 'Desconocido')
    solucion_data['foco_innovacion_nombre'] = focos_dict.get(solucion_data['id_foco_innovacion'], 'Desconocido')

    # Verificar el rol del usuario logueado consultando la tabla 'perfil'
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    # Verificar si el perfil contiene información y si el rol es 'Experto'
    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Si el método es POST, proceder con la eliminación
    if request.method == 'POST':
        mensaje_experto = request.POST.get('mensaje_experto', None)  # Obtener el mensaje opcional

        try:
            # Llamada para eliminar la solución a través de la API
            client.delete_data(where_condition=f"codigo_solucion = {codigo_solucion}")

            # Eliminar el archivo de la carpeta media usando la URL almacenada
            archivo_url = solucion_data.get('archivo_multimedia')  # Obtén la URL del archivo de la base de datos

            # Imprimir para depurar la URL obtenida
            print(f"Archivo multimedia URL: {archivo_url}")

            if archivo_url:
                # Decodificar la URL para obtener la ruta correcta del archivo
                archivo_url_decoded = unquote(archivo_url)
                
                # Corregir la construcción de la ruta física del archivo eliminando la duplicación de "media"
                archivo_path = os.path.join(settings.MEDIA_ROOT, archivo_url_decoded.lstrip('/media/'))

                # Imprimir para verificar la ruta física del archivo
                print(f"Ruta física del archivo decodificado: {archivo_path}")

                if os.path.exists(archivo_path):
                    print(f"Archivo encontrado. Procediendo a eliminarlo.")
                    os.remove(archivo_path)
                    messages.success(request, 'Archivo de solución eliminado con éxito.')
                else:
                    print(f"El archivo no existe en la ruta: {archivo_path}")
                    messages.warning(request, 'El archivo no se encontró en la carpeta media.')
            else:
                print("No se encontró la URL del archivo multimedia.")

            # Crear la notificación con el mensaje del experto (si se proporciona)
            create_notification(user_email, 'solucion', solucion_data['titulo'], 'eliminar', solucion_data['creador_por'], mensaje_experto)

            # Mostrar mensaje de éxito y redirigir a la lista de soluciones
            messages.success(request, 'Solución eliminada con éxito.')
            return redirect('soluciones:list_soluciones')

        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP al eliminar la solución: {e}")
            messages.error(request, f'Error HTTP al eliminar la solución: {e}')
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud HTTP: {e}")
            messages.error(request, f'Error en la solicitud HTTP: {e}')
        except Exception as e:
            print(f"Error inesperado al eliminar la solución: {e}")
            messages.error(request, f'Error inesperado al eliminar la solución: {e}')

    # Si no es POST, mostrar la vista de confirmación de eliminación
    return render(request, 'soluciones/delete_soluciones.html', {'solucion': solucion_data, 'is_experto': is_experto})







def detail_solucion(request, codigo_solucion):
    user_email = request.session.get('user_email')

    # Verificar si el email de usuario está presente en la sesión
    if not user_email:
        return redirect('login:login')

    try:
        # Instancia del cliente API para obtener la solución
        client = APIClient('solucion')  # Cambiar 'oportunidad' por 'solucion'
        
        # Obtener la solución desde la API
        solucion_response = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")  # Cambiar 'codigo_oportunidad' por 'codigo_solucion'
        
        # Verificar si la solución existe
        if not solucion_response:
            return render(request, 'soluciones/detail_soluciones.html', {'error': 'Solución no encontrada.'})

        # Suponemos que la respuesta contiene los datos de la solución
        solucion_data = solucion_response[0]  # Se espera que sea un diccionario
        
        # Extraer los ID de tipo y foco de innovación
        id_tipo_innovacion = solucion_data.get('id_tipo_innovacion')
        id_foco_innovacion = solucion_data.get('id_foco_innovacion')

        # Obtener los focos y tipos de innovación desde las APIs
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()

        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Obtener los nombres de tipo y foco por los IDs
        tipo_innovacion_nombre = tipos_dict.get(id_tipo_innovacion, 'Desconocido')
        foco_innovacion_nombre = focos_dict.get(id_foco_innovacion, 'Desconocido')

        # Añadir los nombres de tipo y foco a la solución
        solucion_data['tipo_innovacion_nombre'] = tipo_innovacion_nombre
        solucion_data['foco_innovacion_nombre'] = foco_innovacion_nombre

        # Obtener el perfil del usuario logueado
        api_client_perfil = APIClient(table_name="perfil")
        perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

        # Verificar el rol del usuario
        if perfil_data:
            rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
            is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
        else:
            is_experto = False  # En caso de que no se encuentre el perfil

        # Generar la URL del archivo multimedia si existe
        archivo_multimedia = solucion_data.get('archivo_multimedia')
        if archivo_multimedia:
            # Asegúrate de pasar la URL completa utilizando MEDIA_URL
            solucion_data['archivo_multimedia_url'] = f"{settings.MEDIA_URL}{archivo_multimedia}"
        else:
            solucion_data['archivo_multimedia_url'] = None

        # Pasar todos los datos a la plantilla
        return render(request, 'soluciones/detail_soluciones.html', {
            'solucion': solucion_data,
            'tipo_innovacion': tipo_innovacion_nombre,
            'foco_innovacion': foco_innovacion_nombre,
            'is_experto': is_experto,
        })

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render(request, 'soluciones/detail_soluciones.html', {'error': f'Error al cargar los detalles: {e}'})








def update_solucion(request, codigo_solucion):
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para actualizar una solución.')
        return redirect('login:login')

    # Verificar si el usuario es experto
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Llamada a la API para obtener los datos de la solución
    client = APIClient('solucion')
    solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")

    if not solucion:
        messages.error(request, 'Solución no encontrada.')
        return redirect('soluciones:list_soluciones')

    solucion_data = solucion[0]  # Asumimos que es una lista de diccionarios

    # Obtener focos y tipos de innovación
    try:
        focos_innovacion = FocoInnovacionAPI.get_focos()
        tipos_innovacion = TipoInnovacionAPI.get_tipo_innovacion()

        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos_innovacion}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos_innovacion}

        # Añadir los nombres de tipo y foco a los datos de la solución
        solucion_data['tipo_innovacion_nombre'] = tipos_dict.get(solucion_data['id_tipo_innovacion'], 'Desconocido')
        solucion_data['foco_innovacion_nombre'] = focos_dict.get(solucion_data['id_foco_innovacion'], 'Desconocido')

    except Exception as e:
        messages.error(request, f'Error al obtener datos de innovación: {e}')
        return redirect('soluciones:list_soluciones')

    # Procesamiento del formulario
    if request.method == 'POST':
        form = SolucionesUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_data = {
                    'titulo': form.cleaned_data['titulo'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'palabras_claves': form.cleaned_data['palabras_claves'],
                    'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                    'fecha_creacion': solucion_data['fecha_creacion'],  # Mantener la fecha original
                    'id_foco_innovacion': form.cleaned_data['id_foco_innovacion'],
                    'id_tipo_innovacion': form.cleaned_data['id_tipo_innovacion'],
                    'creador_por': solucion_data['creador_por'],  # Mantener al creador original
                    'desarrollador_por': form.cleaned_data.get('desarrollador_por', solucion_data['desarrollador_por']),
                    'area_unidad_desarrollo': form.cleaned_data.get('area_unidad_desarrollo', solucion_data['area_unidad_desarrollo'])
                }

                # Adjuntar archivo multimedia si existe
                if 'archivo_multimedia' in request.FILES:
                    file = request.FILES['archivo_multimedia']
                    
                    # Obtener el nombre del archivo y la ruta completa dentro de media
                    file_name = file.name
                    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    
                    # Guardar el archivo directamente en la carpeta 'media'
                    with open(file_path, 'wb') as f:
                        for chunk in file.chunks():
                            f.write(chunk)
                    
                    # Agregar el nombre del archivo a los datos de json
                    json_data['archivo_multimedia'] = file_name
                else:
                    json_data['archivo_multimedia'] = solucion_data['archivo_multimedia']

                # Actualizar datos en la API
                response = client.auto_update_data(where_condition=f"codigo_solucion = {codigo_solucion}", json_data=json_data)

                if response:
                    # Crear notificación después de actualizar la solución
                    create_notification(
                        experto_email=user_email,
                        tipo_entidad='solucion',
                        entidad_titulo=form.cleaned_data['titulo'],
                        accion='editar',
                        usuario_email=solucion_data['creador_por'],
                        mensaje_experto=form.cleaned_data.get('mensaje_experto', '')
                    )

                    messages.success(request, 'Solución actualizada con éxito.')
                    return redirect('soluciones:list_soluciones')
                else:
                    messages.info(request, 'No hubo cambios en los datos.')

            except Exception as e:
                messages.error(request, f'Error al actualizar la solución: {e}')
        else:
            messages.error(request, 'Formulario inválido. Por favor, revisa los datos ingresados.')
    else:
        # Inicializar formulario con datos actuales
        solucion_data['fecha_creacion'] = solucion_data['fecha_creacion'].split('T')[0]  # Convertir a formato 'YYYY-MM-DD'
        form = SolucionesUpdateForm(initial=solucion_data)

        # Si el usuario no es experto, eliminar el campo 'mensaje_experto'
        if not is_experto:
            form.fields.pop('mensaje_experto', None)

    return render(request, 'soluciones/update_soluciones.html', {'form': form, 'is_experto': is_experto})




def create_notification(experto_email, tipo_entidad, entidad_titulo, accion, usuario_email, mensaje_experto=None):
    try:
        # Diccionario para los mensajes predeterminados
        mensajes = {
            'eliminar': f"El experto ha eliminado tu {tipo_entidad}: {entidad_titulo}",
            'editar': f"El experto ha editado tu {tipo_entidad}: {entidad_titulo}",
            'confirmar': f"El experto ha confirmado tu {tipo_entidad}: {entidad_titulo}",
            'actualizar': f"El experto ha actualizado tu {tipo_entidad}: {entidad_titulo}"
        }

        # Obtener el mensaje predeterminado según la acción
        mensaje_default = mensajes.get(accion, "Acción desconocida")
        print(f"Mensaje predeterminado para la acción '{accion}': {mensaje_default}")

        # Usar el mensaje del experto si se proporciona, de lo contrario, el mensaje predeterminado
        mensaje_final = mensaje_experto if mensaje_experto else mensaje_default
        print(f"Mensaje final a enviar: {mensaje_final}")

        # Verificar si usuario_email es None
        if not usuario_email:
            print("Error: 'usuario_email' no puede ser None.")
            return  # Salir de la función si el correo del usuario es None

        # Crear los datos de la notificación
        notificacion_data = {
            'usuario_email': usuario_email,  # Correo del creador de la entidad
            'tipo_entidad': tipo_entidad,  # Tipo de entidad (idea u oportunidad)
            'entidad_titulo': entidad_titulo,  # Título de la entidad
            'mensaje_default': mensaje_default,
            'mensaje_experto': mensaje_final,  # Usar el mensaje final
            'experto_email': experto_email,  # Correo del experto que realizó la acción
            'fecha_creacion': datetime.now().isoformat(),  # Convertir la fecha a formato ISO
            'leida': False,  # Inicialmente la notificación no ha sido leída
            'accion': accion  # Acción realizada: eliminar, editar, confirmar
        }

        print("Datos de la notificación que se van a enviar:")
        print(notificacion_data)

        # Crear el cliente de la API con el nombre de la tabla 'notificaciones'
        client = APIClient('notificaciones')
        print("Cliente de API creado, intentando insertar los datos...")

        # Insertar la notificación
        response = client.insert_data(json_data=notificacion_data)
        print(f"Respuesta de la API: {response}")

        # Verificar si la notificación fue creada correctamente
        if response:
            print("Notificación creada con éxito.")
        else:
            print("Error al crear la notificación.")
    
    except Exception as e:
        print(f"Error al crear la notificación: {e}")




# def confirmar_solucion(request, codigo_solucion):
#     user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
#     if not user_email:
#         messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para confirmar la solución.')
#         return redirect('login:login')

#     # Verificar si el usuario es experto
#     api_client_perfil = APIClient(table_name="perfil")
#     perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

#     if perfil_data:
#         rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
#         is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
#     else:
#         is_experto = False  # En caso de que no se encuentre el perfil

#     # Llamada a la API para obtener los datos de la solución
#     client = APIClient('solucion')
#     solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")

#     if not solucion:
#         messages.error(request, 'Solución no encontrada.')
#         return redirect('soluciones:list_soluciones')

#     solucion_data = solucion[0]  # Asumimos que es una lista de diccionarios

#     # Verificación de creador_por (en lugar de usuario_email)
#     usuario_email = solucion_data.get('creador_por')
#     if not usuario_email:
#         print(f"Error: 'creador_por' no encontrado en los datos de la solución: {solucion_data}")
#         messages.error(request, 'No se encontró el correo del usuario asociado a esta solución.')
#         return redirect('soluciones:list_soluciones')

#     # Procesamiento del formulario
#     if request.method == 'POST':
#         # Verificar si el usuario está en el segundo paso (confirmar)
#         if 'confirmar' in request.POST:
#             try:
#                 # Obtener el mensaje del experto, si no está presente asignar un valor por defecto
#                 mensaje_experto = request.POST.get('mensaje_experto', "¡Solución confirmada exitosamente!")

#                 # Depuración para ver si el mensaje_experto se captura correctamente
#                 print(f"Mensaje del experto capturado: {mensaje_experto}")  # Ver en la consola de desarrollo

#                 # Cambiar el estado de la solución a True (confirmado)
#                 json_data = {
#                     'estado': True
#                 }

#                 # Actualizar datos en la API
#                 response = client.auto_update_data(where_condition=f"codigo_solucion = {codigo_solucion}", json_data=json_data)

#                 if response:
#                     # Crear la notificación después de confirmar la solución
#                     experto_email = user_email  # Asumimos que el experto es el usuario actual
#                     tipo_entidad = "solución"
#                     entidad_titulo = solucion_data.get('titulo')  # Título de la solución
#                     accion = 'confirmar'

#                     # Llamada a la función para crear la notificación
#                     create_notification(
#                         experto_email=experto_email,
#                         tipo_entidad=tipo_entidad,
#                         entidad_titulo=entidad_titulo,
#                         accion=accion,
#                         usuario_email=usuario_email,
#                         mensaje_experto=mensaje_experto  # Pasar el mensaje_experto aquí
#                     )

#                     messages.success(request, 'La solución ha sido confirmada exitosamente.')
#                     return redirect('soluciones:list_soluciones')
#                 else:
#                     messages.error(request, 'Hubo un error al confirmar la solución.')

#             except Exception as e:
#                 messages.error(request, f'Error al confirmar la solución: {e}')
#         else:
#             # Si no es el segundo paso, mostrar el formulario de confirmación
#             return render(request, 'soluciones/confirmar_solucion.html', {'solucion': solucion_data, 'is_experto': is_experto})








def confirmar_solucion(request, codigo_solucion):
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para confirmar la solución.')
        return redirect('login:login')

    # Verificar si el usuario es experto
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Llamada a la API para obtener los datos de la solución
    client = APIClient('solucion')
    solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")

    if not solucion:
        messages.error(request, 'Solución no encontrada.')
        return redirect('soluciones:list_soluciones')

    solucion_data = solucion[0]  # Asumimos que es una lista de diccionarios

    # Verificación de creador_por (en lugar de usuario_email)
    usuario_email = solucion_data.get('creador_por')
    if not usuario_email:
        print(f"Error: 'creador_por' no encontrado en los datos de la solución: {solucion_data}")
        messages.error(request, 'No se encontró el correo del usuario asociado a esta solución.')
        return redirect('soluciones:list_soluciones')

    # Procesamiento del formulario
    if request.method == 'POST':
        # Verificar si el usuario está en el segundo paso (confirmar)
        if 'confirmar' in request.POST:
            try:
                # Obtener el mensaje del experto, si no está presente asignar un valor por defecto
                mensaje_experto = request.POST.get('mensaje_experto', "¡Solución confirmada exitosamente!")

                # Cambiar el estado de la solución a True (confirmado)
                json_data = {
                    'estado': True
                }

                # Actualizar datos en la API
                response = client.auto_update_data(where_condition=f"codigo_solucion = {codigo_solucion}", json_data=json_data)

                if response:
                    # Crear la notificación después de confirmar la solución
                    experto_email = user_email  # Asumimos que el experto es el usuario actual
                    tipo_entidad = "solución"
                    entidad_titulo = solucion_data.get('titulo')  # Título de la solución
                    accion = 'confirmar'

                    # Llamada a la función para crear la notificación
                    create_notification(
                        experto_email=experto_email,
                        tipo_entidad=tipo_entidad,
                        entidad_titulo=entidad_titulo,
                        accion=accion,
                        usuario_email=usuario_email,
                        mensaje_experto=mensaje_experto  # Pasar el mensaje_experto aquí
                    )

                    # Transferir solución a proyecto si se confirma
                    print("Confirmación exitosa, transfiriendo solución a proyecto...")

                    proyecto_client = APIClient('proyecto')
                    fecha_aprobacion = timezone.now().isoformat()

                    # Crear los datos del proyecto
                    proyecto_data = {
                        "tipo_origen": "solución",  # Indicar que es una solución
                        "id_origen": codigo_solucion,
                        "titulo": solucion_data.get('titulo'),
                        "descripcion": solucion_data.get('descripcion'),
                        "fecha_creacion": solucion_data.get('fecha_creacion'),
                        "palabras_claves": solucion_data.get('palabras_claves'),
                        "recursos_requeridos": solucion_data.get('recursos_requeridos'),
                        "archivo_multimedia": solucion_data.get('archivo_multimedia'),
                        "creador_por": solucion_data.get('creador_por'),
                        "id_tipo_innovacion": solucion_data.get('id_tipo_innovacion'),
                        "id_foco_innovacion": solucion_data.get('id_foco_innovacion'),
                        "estado": True,
                        "fecha_aprobacion": fecha_aprobacion,
                        "aprobado_por": user_email,
                        # Datos adicionales para la solución
                        "desarrollador_por": solucion_data.get('desarrollador_por'),
                        "area_unidad_desarrollo": solucion_data.get('area_unidad_desarrollo'),
                    }

                    print(f"Datos del proyecto a insertar: {proyecto_data}")

                    proyecto_response = proyecto_client.insert_data(json_data=proyecto_data)
                    print(f"Respuesta de inserción de proyecto: {proyecto_response}")

                    if proyecto_response:
                        messages.success(request, 'La solución ha sido confirmada y transferida a proyecto exitosamente.')
                        return redirect('soluciones:list_soluciones')
                    else:
                        messages.error(request, 'La solución fue confirmada, pero hubo un error al crear el proyecto.')

                else:
                    messages.error(request, 'Hubo un error al confirmar la solución.')

            except Exception as e:
                messages.error(request, f'Error al confirmar la solución: {e}')
        else:
            # Si no es el segundo paso, mostrar el formulario de confirmación
            return render(request, 'soluciones/confirmar_solucion.html', {'solucion': solucion_data, 'is_experto': is_experto})
