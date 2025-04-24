from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime
from werkzeug.utils import secure_filename
from urllib.parse import unquote
import os, json, requests
from flask_login import login_required, current_user
import mysql.connector
from config_flask import DATABASE_CONFIG

#from models.api_client import APIClient, FocoInnovacionAPI, TipoInnovacionAPI
#from forms.formsSoluciones import SolucionesForm
#from utils.notificaciones import create_notification
from forms.formsSoluciones.formsSoluciones import SolucionesUpdateForm




vistaSolucion = Blueprint('vistaSolucion', __name__, template_folder='../templates/soluciones')

@vistaSolucion.route('/listado', methods=['GET'])
def list_soluciones():
    user_email = session.get('user_email')

    if not user_email:
        return redirect(url_for('login.login'))

    # Crear instancia de APIClient para la tabla 'solucion'
    client = APIClient('solucion')

    # Obtener tipos de innovación y focos de innovación usando las clases de API específicas
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Obtener los valores de los filtros
    selected_tipo = request.args.get('tipo_innovacion', '')
    selected_foco = request.args.get('foco_innovacion', '')
    selected_estado = request.args.get('estado', '')

    # Crear condición WHERE
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
        soluciones = client.get_data(where_condition=where_condition)

        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        for solucion in soluciones:
            solucion['tipo_innovacion_nombre'] = tipos_dict.get(solucion.get('id_tipo_innovacion'), 'Desconocido')
            solucion['foco_innovacion_nombre'] = focos_dict.get(solucion.get('id_foco_innovacion'), 'Desconocido')

            fecha_creacion = solucion.get('fecha_creacion')
            if fecha_creacion:
                try:
                    solucion['fecha_creacion'] = datetime.strptime(
                        fecha_creacion, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%Y-%m-%d")
                except ValueError:
                    solucion['fecha_creacion'] = "Fecha inválida"

        if not soluciones:
            flash('No hay soluciones disponibles.', 'info')
        else:
            flash(f'Se obtuvieron {len(soluciones)} soluciones.', 'info')

    except Exception as e:
        flash(f'Error al obtener las soluciones: {e}', 'danger')
        soluciones = []

    # Verificar rol
    perfil_client = APIClient('perfil')
    perfil_data = perfil_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil_data and perfil_data[0].get('rol', '').lower() == 'experto'

    return render_template('soluciones/list_soluciones.html',
                           soluciones=soluciones,
                           tipos=tipos,
                           focos=focos,
                           selected_tipo=selected_tipo,
                           selected_foco=selected_foco,
                           selected_estado=selected_estado,
                           user_email=user_email,
                           is_experto=is_experto)


def insertar_solucion_usuario(user_email, solucion_codigo):
    try:
        # Usamos el cliente API para insertar la relación
        client = APIClient('usuario_solucion')  # Asegúrate de que este sea el nombre correcto de la tabla en tu API
        json_data = {
            'email_usuario': user_email,
            'codigo_solucion': solucion_codigo
        }
        response = client.insert_data(json_data=json_data)

        if response:
            print(f"Relación creada con éxito: Usuario {user_email} - Solución {solucion_codigo}")
        else:
            print("La API no devolvió respuesta.")
    except Exception as e:
        print(f"Error al insertar la relación: {e}")


@vistaSolucion.route('/crear', methods=['GET', 'POST'])
def create_solucion():
    print("Iniciando la vista create_solucion")
    
    # Verificar si el usuario ha iniciado sesión
    user_email = session.get('user_email')
    if not user_email:
        flash('No has iniciado sesión. Por favor, inicia sesión para crear una solución.', 'error')
        return redirect(url_for('login.login'))

    focos_innovacion, tipos_innovacion = [], []

    try:
        client_foco = APIClient('foco_innovacion')
        focos_innovacion = client_foco.get_data()
        if isinstance(focos_innovacion, dict) and 'result' in focos_innovacion:
            focos_innovacion = json.loads(focos_innovacion['result'][0]['result'])

        client_tipo = APIClient('tipo_innovacion')
        tipos_innovacion = client_tipo.get_data()
        if isinstance(tipos_innovacion, dict) and 'result' in tipos_innovacion:
            tipos_innovacion = json.loads(tipos_innovacion['result'][0]['result'])

    except Exception as e:
        flash(f"Error al obtener focos o tipos de innovación: {e}", 'error')

    form = SolucionesForm()

    if request.method == 'POST' and form.validate_on_submit():
        foco_id = int(form.id_foco_innovacion.data)
        tipo_id = int(form.id_tipo_innovacion.data)

        foco_innovacion = next((f for f in focos_innovacion if f['id_foco_innovacion'] == foco_id), None)
        tipo_innovacion = next((t for t in tipos_innovacion if t['id_tipo_innovacion'] == tipo_id), None)

        json_data = {
            'titulo': form.titulo.data,
            'descripcion': form.descripcion.data,
            'fecha_creacion': form.fecha_creacion.data.isoformat(),
            'id_foco_innovacion': foco_innovacion['id_foco_innovacion'] if foco_innovacion else None,
            'id_tipo_innovacion': tipo_innovacion['id_tipo_innovacion'] if tipo_innovacion else None,
            'creador_por': user_email,
            'palabras_claves': form.palabras_claves.data,
            'recursos_requeridos': form.recursos_requeridos.data,
            'desarrollador_por': form.desarrollador_por.data,
            'area_unidad_desarrollo': form.area_unidad_desarrollo.data
        }

        if form.archivo_multimedia.data:
            file = form.archivo_multimedia.data
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))
            json_data['archivo_multimedia'] = f'/static/uploads/{filename}'

        try:
            client = APIClient('solucion')
            response = client.insert_data(json_data=json_data)
            if response and 'outputParams' in response and response['outputParams'].get('mensaje') == "Inserción realizada correctamente.":
                flash('Solución creada con éxito.', 'success')
                return redirect(url_for('soluciones.list_soluciones'))
            else:
                flash(f"Error al crear solución: {response}", 'error')
        except Exception as e:
            flash(f"Error al conectar con la API: {e}", 'error')

    return render_template('soluciones/create.html', form=form, focos_innovacion=focos_innovacion, tipos_innovacion=tipos_innovacion)


# Simulación de la función create_notification (puedes moverla a un módulo utils si es necesario)
def create_notification(usuario, modulo, titulo, accion, destinatario, mensaje=None):
    print(f"Notificación: [{modulo}] {usuario} realizó {accion} sobre {titulo}. Destinatario: {destinatario}. Mensaje: {mensaje}")

@vistaSolucion.route('/soluciones/eliminar/<int:codigo_solucion>', methods=['GET', 'POST'])
def delete_solucion(codigo_solucion):
    user_email = session.get('user_email')
    if not user_email:
        flash('No has iniciado sesión. Por favor, inicia sesión para eliminar una solución.', 'error')
        return redirect(url_for('login'))

    client = APIClient('solucion')
    solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")

    if not solucion:
        flash('Solución no encontrada.', 'error')
        return redirect(url_for('soluciones.list_soluciones'))

    solucion_data = solucion[0]
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()
    focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
    tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}
    solucion_data['tipo_innovacion_nombre'] = tipos_dict.get(solucion_data['id_tipo_innovacion'], 'Desconocido')
    solucion_data['foco_innovacion_nombre'] = focos_dict.get(solucion_data['id_foco_innovacion'], 'Desconocido')

    perfil_client = APIClient('perfil')
    perfil_data = perfil_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil_data and perfil_data[0].get('rol') == 'Experto'

    if request.method == 'POST':
        mensaje_experto = request.form.get('mensaje_experto')

        try:
            client.delete_data(where_condition=f"codigo_solucion = {codigo_solucion}")
            archivo_url = solucion_data.get('archivo_multimedia')

            if archivo_url:
                archivo_url_decoded = unquote(archivo_url)
                archivo_path = os.path.join(MEDIA_ROOT, archivo_url_decoded.lstrip('/media/'))
                if os.path.exists(archivo_path):
                    os.remove(archivo_path)
                    flash('Archivo de solución eliminado con éxito.', 'success')
                else:
                    flash('El archivo no se encontró en la carpeta media.', 'warning')

            create_notification(user_email, 'solucion', solucion_data['titulo'], 'eliminar', solucion_data['creador_por'], mensaje_experto)
            flash('Solución eliminada con éxito.', 'success')
            return redirect(url_for('soluciones.list_soluciones'))

        except requests.exceptions.RequestException as e:
            flash(f'Error en la solicitud HTTP: {e}', 'error')
        except Exception as e:
            flash(f'Error inesperado al eliminar la solución: {e}', 'error')

    return render_template('soluciones/delete_soluciones.html', solucion=solucion_data, is_experto=is_experto)

@vistaSolucion.route('/detalle/<int:codigo_solucion>')
def detail_solucion(codigo_solucion):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    try:
        client = APIClient('solucion')
        solucion_response = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")

        if not solucion_response:
            return render_template('soluciones/detail_soluciones.html', error='Solución no encontrada.')

        solucion_data = solucion_response[0]
        id_tipo_innovacion = solucion_data.get('id_tipo_innovacion')
        id_foco_innovacion = solucion_data.get('id_foco_innovacion')

        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()

        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        tipo_innovacion_nombre = tipos_dict.get(id_tipo_innovacion, 'Desconocido')
        foco_innovacion_nombre = focos_dict.get(id_foco_innovacion, 'Desconocido')

        solucion_data['tipo_innovacion_nombre'] = tipo_innovacion_nombre
        solucion_data['foco_innovacion_nombre'] = foco_innovacion_nombre

        api_client_perfil = APIClient(table_name="perfil")
        perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

        if perfil_data:
            rol_usuario = perfil_data[0].get('rol')
            is_experto = (rol_usuario == 'Experto')
        else:
            is_experto = False

        archivo_multimedia = solucion_data.get('archivo_multimedia')
        if archivo_multimedia:
            media_url = current_app.config.get('MEDIA_URL', '/media/')
            solucion_data['archivo_multimedia_url'] = f"{media_url}{archivo_multimedia}"
        else:
            solucion_data['archivo_multimedia_url'] = None

        return render_template('soluciones/detail_soluciones.html',
                               solucion=solucion_data,
                               tipo_innovacion=tipo_innovacion_nombre,
                               foco_innovacion=foco_innovacion_nombre,
                               is_experto=is_experto)

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template('soluciones/detail_soluciones.html', error=f"Error al cargar los detalles: {e}")

@vistaSolucion.route('/solucion/update/<int:codigo_solucion>', methods=['GET', 'POST'])
def update_solucion(codigo_solucion):
    user_email = session.get('user_email')
    if not user_email:
        flash('No has iniciado sesión. Por favor, inicia sesión para actualizar una solución.', 'error')
        return redirect(url_for('login'))

    # Verificar si el usuario es experto
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil_data and perfil_data[0].get('rol') == 'Experto'

    # Obtener la solución actual
    client = APIClient('solucion')
    solucion = client.get_data(where_condition=f"codigo_solucion = {codigo_solucion}")
    if not solucion:
        flash('Solución no encontrada.', 'error')
        return redirect(url_for('vistaSolucion.list_soluciones'))

    solucion_data = solucion[0]

    # Obtener focos y tipos de innovación
    try:
        focos_innovacion = FocoInnovacionAPI.get_focos()
        tipos_innovacion = TipoInnovacionAPI.get_tipo_innovacion()

        focos_dict = {f['id_foco_innovacion']: f['name'] for f in focos_innovacion}
        tipos_dict = {t['id_tipo_innovacion']: t['name'] for t in tipos_innovacion}

        solucion_data['tipo_innovacion_nombre'] = tipos_dict.get(solucion_data['id_tipo_innovacion'], 'Desconocido')
        solucion_data['foco_innovacion_nombre'] = focos_dict.get(solucion_data['id_foco_innovacion'], 'Desconocido')
    except Exception as e:
        flash(f'Error al obtener datos de innovación: {e}', 'error')
        return redirect(url_for('vistaSolucion.list_soluciones'))

    if request.method == 'POST':
        form = SolucionesUpdateForm(request.form)
        if form.validate():
            try:
                json_data = {
                    'titulo': form.titulo.data,
                    'descripcion': form.descripcion.data,
                    'palabras_claves': form.palabras_claves.data,
                    'recursos_requeridos': form.recursos_requeridos.data,
                    'fecha_creacion': solucion_data['fecha_creacion'],
                    'id_foco_innovacion': form.id_foco_innovacion.data,
                    'id_tipo_innovacion': form.id_tipo_innovacion.data,
                    'creador_por': solucion_data['creador_por'],
                    'desarrollador_por': form.desarrollador_por.data,
                    'area_unidad_desarrollo': form.area_unidad_desarrollo.data
                }

                # Archivo multimedia
                if 'archivo_multimedia' in request.files:
                    file = request.files['archivo_multimedia']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                        file.save(file_path)
                        json_data['archivo_multimedia'] = filename
                    else:
                        json_data['archivo_multimedia'] = solucion_data.get('archivo_multimedia')

                response = client.auto_update_data(where_condition=f"codigo_solucion = {codigo_solucion}", json_data=json_data)

                if response:
                    # Crear notificación
                    if is_experto:
                        create_notification(
                            experto_email=user_email,
                            tipo_entidad='solucion',
                            entidad_titulo=form.titulo.data,
                            accion='editar',
                            usuario_email=solucion_data['creador_por'],
                            mensaje_experto=form.mensaje_experto.data if hasattr(form, 'mensaje_experto') else ''
                        )
                    flash('Solución actualizada con éxito.', 'success')
                    return redirect(url_for('vistaSolucion.list_soluciones'))
                else:
                    flash('No hubo cambios en los datos.', 'info')
            except Exception as e:
                flash(f'Error al actualizar la solución: {e}', 'error')
        else:
            flash('Formulario inválido. Por favor, revisa los datos ingresados.', 'error')
    else:
        # GET: Inicializar formulario con datos
        solucion_data['fecha_creacion'] = solucion_data['fecha_creacion'].split('T')[0]
        form = SolucionesUpdateForm(data=solucion_data)
        if not is_experto:
            form.mensaje_experto = None

    return render_template('soluciones/update_soluciones.html', form=form, is_experto=is_experto)

def create_notification(experto_email, tipo_entidad, entidad_titulo, accion, usuario_email, mensaje_experto=None):
    try:
        mensajes = {
            'eliminar': f"El experto ha eliminado tu {tipo_entidad}: {entidad_titulo}",
            'editar': f"El experto ha editado tu {tipo_entidad}: {entidad_titulo}",
            'confirmar': f"El experto ha confirmado tu {tipo_entidad}: {entidad_titulo}",
            'actualizar': f"El experto ha actualizado tu {tipo_entidad}: {entidad_titulo}"
        }

        mensaje_default = mensajes.get(accion, "Acción desconocida")
        print(f"Mensaje predeterminado para la acción '{accion}': {mensaje_default}")

        mensaje_final = mensaje_experto if mensaje_experto else mensaje_default
        print(f"Mensaje final a enviar: {mensaje_final}")

        if not usuario_email:
            print("Error: 'usuario_email' no puede ser None.")
            return

        notificacion_data = {
            'usuario_email': usuario_email,
            'tipo_entidad': tipo_entidad,
            'entidad_titulo': entidad_titulo,
            'mensaje_default': mensaje_default,
            'mensaje_experto': mensaje_final,
            'experto_email': experto_email,
            'fecha_creacion': datetime.now().isoformat(),
            'leida': False,
            'accion': accion
        }

        print("Datos de la notificación que se van a enviar:")
        print(notificacion_data)

        client = APIClient('notificaciones')
        print("Cliente de API creado, intentando insertar los datos...")

        response = client.insert_data(json_data=notificacion_data)
        print(f"Respuesta de la API: {response}")

        if response:
            print("Notificación creada con éxito.")
        else:
            print("Error al crear la notificación.")

    except Exception as e:
        print(f"Error al crear la notificación: {e}")

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

soluciones_bp = Blueprint('soluciones', __name__)

@soluciones_bp.route('/soluciones/crear', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
            cursor = conn.cursor()
            
            # Aquí iría la lógica para crear una solución
            # Por ahora solo mostramos un mensaje de éxito
            flash('Solución creada exitosamente', 'success')
            return redirect(url_for('soluciones.create'))
            
        except Exception as e:
            flash(f'Error al crear la solución: {str(e)}', 'danger')
        finally:
            if 'conn' in locals():
                conn.close()
    
    return render_template('templatesSoluciones/create.html')

@soluciones_bp.route('/soluciones/calendario')
@login_required
def calendario():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        # Aquí iría la lógica para obtener el calendario
        # Por ahora solo renderizamos la plantilla
        return render_template('templatesSoluciones/calendario.html')
        
    except Exception as e:
        flash(f'Error al cargar el calendario: {str(e)}', 'danger')
        return redirect(url_for('soluciones.create'))
    finally:
        if 'conn' in locals():
            conn.close()

@soluciones_bp.route('/soluciones/ultimos-lanzamientos')
@login_required
def ultimos_lanzamientos():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        # Aquí iría la lógica para obtener los últimos lanzamientos
        # Por ahora solo renderizamos la plantilla
        return render_template('templatesSoluciones/ultimos_lanzamientos.html')
        
    except Exception as e:
        flash(f'Error al cargar los últimos lanzamientos: {str(e)}', 'danger')
        return redirect(url_for('soluciones.create'))
    finally:
        if 'conn' in locals():
            conn.close()

@soluciones_bp.route('/soluciones/proximos-lanzamientos')
@login_required
def proximos_lanzamientos():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG['mysql'])
        cursor = conn.cursor(dictionary=True)
        
        # Aquí iría la lógica para obtener los próximos lanzamientos
        # Por ahora solo renderizamos la plantilla
        return render_template('templatesSoluciones/proximos_lanzamientos.html')
        
    except Exception as e:
        flash(f'Error al cargar los próximos lanzamientos: {str(e)}', 'danger')
        return redirect(url_for('soluciones.create'))
    finally:
        if 'conn' in locals():
            conn.close()
