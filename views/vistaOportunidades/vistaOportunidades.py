from flask import Flask, request, redirect, render_template, session, flash, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
from urllib.parse import unquote

# Importar tus clientes y módulos necesarios
from app.api_client import APIClient, FocoInnovacionAPI, TipoInnovacionAPI
from app.models import OportunidadUsuario
from app.forms import OportunidadForm
from app.utils import create_notification, insertar_oportunidad_usuario

@app.route('/oportunidades')
def list_oportunidad():
    user_email = session.get('user_email')
    if not user_email:
        flash('Por favor, inicia sesión para ver las oportunidades.', 'warning')
        return redirect(url_for('login'))

    # Obtener filtros desde GET
    selected_tipo = request.args.get('tipo_innovacion', '')
    selected_foco = request.args.get('foco_innovacion', '')
    selected_estado = request.args.get('estado', '')

    # Construir condición WHERE
    filters = []
    if selected_tipo:
        filters.append(f"id_tipo_innovacion = {selected_tipo}")
    if selected_foco:
        filters.append(f"id_foco_innovacion = {selected_foco}")
    if selected_estado != '':
        filters.append(f"estado = {selected_estado.upper()}")

    where_condition = " AND ".join(filters) if filters else None

    # Cargar focos y tipos de innovación
    try:
        tipos = TipoInnovacionAPI.get_tipo_innovacion()
        focos = FocoInnovacionAPI.get_focos()
    except Exception as e:
        flash(f"Error al cargar catálogos: {e}", 'danger')
        tipos = []
        focos = []

    # Cargar oportunidades
    try:
        client = APIClient('oportunidad')
        oportunidades = client.get_data(where_condition=where_condition)

        tipos_dict = {t['id_tipo_innovacion']: t['name'] for t in tipos}
        focos_dict = {f['id_foco_innovacion']: f['name'] for f in focos}

        for o in oportunidades:
            o['tipo_innovacion_nombre'] = tipos_dict.get(o.get('id_tipo_innovacion'), 'Desconocido')
            o['foco_innovacion_nombre'] = focos_dict.get(o.get('id_foco_innovacion'), 'Desconocido')
            fecha = o.get('fecha_creacion')
            try:
                if fecha:
                    fecha = fecha.rstrip('Z')
                    formato = "%Y-%m-%dT%H:%M:%S" if 'T' in fecha else "%Y-%m-%d"
                    o['fecha_creacion'] = datetime.strptime(fecha, formato).strftime("%Y-%m-%d")
            except Exception as e:
                o['fecha_creacion'] = "Fecha inválida"

        if not oportunidades:
            flash('No hay oportunidades disponibles con los filtros seleccionados.', 'info')
        else:
            flash(f'Se encontraron {len(oportunidades)} oportunidades.', 'success')

    except Exception as e:
        oportunidades = []
        flash(f"Error al obtener las oportunidades: {e}", "danger")

    # Verificar si el usuario es experto
    try:
        perfil_client = APIClient('perfil')
        perfil = perfil_client.get_data(where_condition=f"usuario_email = '{user_email}'")
        is_experto = perfil[0]['rol'].lower() == 'experto' if perfil else False
    except Exception as e:
        is_experto = False
        flash(f"Error al verificar el rol del usuario: {e}", 'warning')

    return render_template("lista_oportunidades.html", 
                           oportunidades=oportunidades,
                           tipos=tipos,
                           focos=focos,
                           selected_tipo=selected_tipo,
                           selected_foco=selected_foco,
                           selected_estado=selected_estado,
                           user_email=user_email,
                           is_experto=is_experto)

...

@app.route('/crear_oportunidad', methods=['GET', 'POST'])
def create_oportunidad():
    print("Iniciando la vista create_oportunidad")

    user_email = session.get('user_email')
    if not user_email:
        flash('Debes iniciar sesión para crear una oportunidad.', 'danger')
        return redirect(url_for('login'))

    print(f'Usuario logueado: {user_email}')

    # Obtener focos y tipos desde las APIs
    try:
        client_foco = APIClient('foco_innovacion')
        client_tipo = APIClient('tipo_innovacion')

        focos = client_foco.get_data()
        tipos = client_tipo.get_data()

        if isinstance(focos, dict) and 'result' in focos:
            focos = json.loads(focos['result'][0]['result'])

        if isinstance(tipos, dict) and 'result' in tipos:
            tipos = json.loads(tipos['result'][0]['result'])

        if not focos or not tipos:
            flash('No hay focos o tipos de innovación disponibles.', 'info')

    except Exception as e:
        flash(f'Error al obtener los datos de innovación: {e}', 'danger')
        focos = []
        tipos = []

    # Inicializar formulario
    form = OportunidadForm()
    form.id_foco_innovacion.choices = [(f['id_foco_innovacion'], f['name']) for f in focos]
    form.id_tipo_innovacion.choices = [(t['id_tipo_innovacion'], t['name']) for t in tipos]

    if request.method == 'POST' and form.validate_on_submit():
        print("Formulario válido")
        try:
            foco = next((f for f in focos if f['id_foco_innovacion'] == form.id_foco_innovacion.data), None)
            tipo = next((t for t in tipos if t['id_tipo_innovacion'] == form.id_tipo_innovacion.data), None)

            if not foco or not tipo:
                flash("ID de foco o tipo de innovación no válidos.", 'warning')
                return redirect(url_for('create_oportunidad'))

            json_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'fecha_creacion': form.fecha_creacion.data.isoformat(),
                'id_foco_innovacion': foco['id_foco_innovacion'],
                'id_tipo_innovacion': tipo['id_tipo_innovacion'],
                'creador_por': user_email
            }

            # Procesar archivo multimedia
            if form.archivo_multimedia.data:
                archivo = form.archivo_multimedia.data
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static/uploads', filename)
                archivo.save(filepath)
                json_data['archivo_multimedia'] = f"/static/uploads/{filename}"
                flash(f'Archivo multimedia cargado: {filename}', 'info')

            client = APIClient('oportunidad')
            response = client.insert_data(json_data=json_data)

            if isinstance(response, str):
                response = json.loads(response)

            if 'outputParams' in response and response['outputParams'].get('mensaje') == "Inserción realizada correctamente.":
                # Si todo fue bien, registra la relación con el usuario
                insertar_oportunidad_usuario(user_email, json_data['titulo'])  # Aquí usar código real si está disponible
                flash('¡Oportunidad creada con éxito!', 'success')
                return redirect(url_for('list_oportunidad'))
            else:
                flash(f"Error en la API: {response.get('message', 'Sin mensaje')}", 'danger')

        except Exception as e:
            flash(f"Error al procesar la oportunidad: {e}", 'danger')
    elif request.method == 'POST':
        flash('Formulario inválido. Revisa los datos.', 'warning')

    return render_template('crear_oportunidad.html', form=form, focos_innovacion=focos, tipos_innovacion=tipos)

...

@app.route('/eliminar_oportunidad/<codigo_oportunidad>', methods=['GET', 'POST'])
def delete_oportunidad(codigo_oportunidad):
    user_email = session.get('user_email')
    if not user_email:
        flash('Debes iniciar sesión para eliminar una oportunidad.', 'danger')
        return redirect(url_for('login'))

    client = APIClient('oportunidad')
    oportunidad = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")
    
    if not oportunidad:
        flash('Oportunidad no encontrada.', 'danger')
        return redirect(url_for('list_oportunidad'))

    oportunidad_data = oportunidad[0]

    # Obtener tipos y focos
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()
    focos_dict = {f['id_foco_innovacion']: f['name'] for f in focos}
    tipos_dict = {t['id_tipo_innovacion']: t['name'] for t in tipos}
    oportunidad_data['foco_innovacion_nombre'] = focos_dict.get(oportunidad_data['id_foco_innovacion'], 'Desconocido')
    oportunidad_data['tipo_innovacion_nombre'] = tipos_dict.get(oportunidad_data['id_tipo_innovacion'], 'Desconocido')

    # Verificar si es experto
    perfil_client = APIClient('perfil')
    perfil = perfil_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil and perfil[0].get('rol', '').lower() == 'experto'

    if request.method == 'POST':
        mensaje_experto = request.form.get('mensaje_experto', None)

        try:
            # Eliminar la oportunidad en la API
            client.delete_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")

            # Eliminar archivo multimedia si existe
            archivo_url = oportunidad_data.get('archivo_multimedia')
            print(f"Archivo multimedia URL: {archivo_url}")

            if archivo_url:
                archivo_url_decoded = unquote(archivo_url)
                archivo_path = os.path.join('static/uploads', archivo_url_decoded.split('/')[-1])  # adaptado a Flask

                print(f"Ruta física del archivo decodificado: {archivo_path}")
                if os.path.exists(archivo_path):
                    os.remove(archivo_path)
                    flash('Archivo de oportunidad eliminado correctamente.', 'info')
                else:
                    flash('El archivo no se encontró en el sistema.', 'warning')

            # Crear notificación (si hay mensaje)
            create_notification(
                experto_email=user_email,
                tipo_entidad='oportunidad',
                entidad_titulo=oportunidad_data['titulo'],
                accion='eliminar',
                usuario_email=oportunidad_data['creador_por'],
                mensaje_experto=mensaje_experto
            )

            flash('Oportunidad eliminada con éxito.', 'success')
            return redirect(url_for('list_oportunidad'))

        except Exception as e:
            flash(f'Error al eliminar la oportunidad: {e}', 'danger')

    # Mostrar plantilla de confirmación
    return render_template('eliminar_oportunidad.html', oportunidad=oportunidad_data, is_experto=is_experto)

...


@app.route('/detalle_oportunidad/<codigo_oportunidad>')
def detail_oportunidad(codigo_oportunidad):
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    try:
        oportunidad = OportunidadUsuario.get_oportunidad_by_codigo(codigo_oportunidad)

        if not oportunidad or 'codigo_oportunidad' not in oportunidad:
            return render_template('detalle_oportunidad.html', error='Oportunidad no encontrada o datos no disponibles.')

        id_tipo = oportunidad.get('id_tipo_innovacion')
        id_foco = oportunidad.get('id_foco_innovacion')

        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()

        tipos_dict = {t['id_tipo_innovacion']: t['name'] for t in tipos}
        focos_dict = {f['id_foco_innovacion']: f['name'] for f in focos}

        tipo_nombre = tipos_dict.get(id_tipo, 'Desconocido')
        foco_nombre = focos_dict.get(id_foco, 'Desconocido')

        oportunidad['tipo_innovacion_nombre'] = tipo_nombre
        oportunidad['foco_innovacion_nombre'] = foco_nombre

        archivo = oportunidad.get('archivo_multimedia')
        if archivo:
            oportunidad['archivo_multimedia_url'] = f"/static/uploads/{archivo.split('/')[-1]}"
        else:
            oportunidad['archivo_multimedia_url'] = None

        return render_template('detalle_oportunidad.html',
                               oportunidad=oportunidad,
                               tipo_innovacion=tipo_nombre,
                               foco_innovacion=foco_nombre)

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template('detalle_oportunidad.html', error=f"Error al cargar los detalles: {e}")

...

@app.route('/editar_oportunidad/<codigo_oportunidad>', methods=['GET', 'POST'])
def update_oportunidad(codigo_oportunidad):
    user_email = session.get('user_email')
    if not user_email:
        flash('Debes iniciar sesión para editar una oportunidad.', 'warning')
        return redirect(url_for('login'))

    # Verificar si es experto
    perfil_client = APIClient('perfil')
    perfil_data = perfil_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    is_experto = perfil_data and perfil_data[0].get('rol', '').lower() == 'experto'

    # Obtener oportunidad actual
    client = APIClient('oportunidad')
    oportunidad_list = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")

    if not oportunidad_list:
        flash('Oportunidad no encontrada.', 'danger')
        return redirect(url_for('list_oportunidad'))

    oportunidad_data = oportunidad_list[0]

    # Obtener catálogos
    try:
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()
    except Exception as e:
        flash(f'Error al cargar datos de innovación: {e}', 'danger')
        return redirect(url_for('list_oportunidad'))

    # Preparar formulario
    form = OportunidadForm(data=oportunidad_data)
    form.id_foco_innovacion.choices = [(f['id_foco_innovacion'], f['name']) for f in focos]
    form.id_tipo_innovacion.choices = [(t['id_tipo_innovacion'], t['name']) for t in tipos]

    if not is_experto and hasattr(form, 'mensaje_experto'):
        del form.mensaje_experto

    if request.method == 'POST' and form.validate_on_submit():
        try:
            json_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'fecha_creacion': form.fecha_creacion.data.isoformat(),
                'id_foco_innovacion': form.id_foco_innovacion.data,
                'id_tipo_innovacion': form.id_tipo_innovacion.data,
                'creador_por': oportunidad_data['creador_por']
            }

            # Manejar archivo multimedia
            if form.archivo_multimedia.data:
                archivo = form.archivo_multimedia.data
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static/uploads', filename)
                archivo.save(filepath)
                json_data['archivo_multimedia'] = f"/static/uploads/{filename}"
            else:
                json_data['archivo_multimedia'] = oportunidad_data.get('archivo_multimedia')

            # Actualizar vía API
            client.auto_update_data(
                where_condition=f"codigo_oportunidad = {codigo_oportunidad}",
                json_data=json_data
            )

            # Notificación si es experto
            if is_experto and hasattr(form, 'mensaje_experto'):
                create_notification(
                    experto_email=user_email,
                    tipo_entidad='oportunidad',
                    entidad_titulo=form.titulo.data,
                    accion='editar',
                    usuario_email=oportunidad_data['creador_por'],
                    mensaje_experto=form.mensaje_experto.data
                )

            flash('Oportunidad actualizada correctamente.', 'success')
            return redirect(url_for('list_oportunidad'))

        except Exception as e:
            flash(f'Error al actualizar la oportunidad: {e}', 'danger')

    return render_template('editar_oportunidad.html',
                           form=form,
                           is_experto=is_experto,
                           codigo_oportunidad=codigo_oportunidad)

...

if request.method == 'POST':
    form = OportunidadForm(request.form, request.files)
    form.id_foco_innovacion.choices = [(f['id_foco_innovacion'], f['name']) for f in focos]
    form.id_tipo_innovacion.choices = [(t['id_tipo_innovacion'], t['name']) for t in tipos]

    if not is_experto and hasattr(form, 'mensaje_experto'):
        del form.mensaje_experto

    if form.validate_on_submit():
        try:
            json_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'fecha_creacion': form.fecha_creacion.data.isoformat(),
                'id_foco_innovacion': form.id_foco_innovacion.data,
                'id_tipo_innovacion': form.id_tipo_innovacion.data,
                'creador_por': oportunidad_data['creador_por']
            }

            # Adjuntar archivo multimedia si se subió
            if form.archivo_multimedia.data:
                archivo = form.archivo_multimedia.data
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static/uploads', filename)
                archivo.save(filepath)
                json_data['archivo_multimedia'] = filename
            else:
                json_data['archivo_multimedia'] = oportunidad_data.get('archivo_multimedia')

            # Actualizar en la API
            response = client.auto_update_data(
                where_condition=f"codigo_oportunidad = {codigo_oportunidad}",
                json_data=json_data
            )

            if response:
                mensaje_experto = getattr(form, 'mensaje_experto', None)
                mensaje = mensaje_experto.data if mensaje_experto else None
                print(f"mensaje_experto recibido: {mensaje}")

                if is_experto and mensaje:
                    create_notification(
                        experto_email=user_email,
                        tipo_entidad='oportunidad',
                        entidad_titulo=form.titulo.data,
                        accion='editar',
                        usuario_email=oportunidad_data['creador_por'],
                        mensaje_experto=mensaje
                    )

                flash('Oportunidad actualizada con éxito.', 'success')
                return redirect(url_for('list_oportunidad'))
            else:
                flash('No hubo cambios en los datos.', 'info')

        except Exception as e:
            flash(f'Error al actualizar la oportunidad: {e}', 'danger')
    else:
        flash('Formulario inválido. Por favor, revisa los datos ingresados.', 'warning')

...

if request.method == 'POST':
    form = OportunidadForm(request.form, request.files)
    form.id_foco_innovacion.choices = [(f['id_foco_innovacion'], f['name']) for f in focos]
    form.id_tipo_innovacion.choices = [(t['id_tipo_innovacion'], t['name']) for t in tipos]

    if not is_experto and hasattr(form, 'mensaje_experto'):
        del form.mensaje_experto

    if form.validate_on_submit():
        try:
            json_data = {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'palabras_claves': form.palabras_claves.data,
                'recursos_requeridos': form.recursos_requeridos.data,
                'fecha_creacion': form.fecha_creacion.data.isoformat(),
                'id_foco_innovacion': form.id_foco_innovacion.data,
                'id_tipo_innovacion': form.id_tipo_innovacion.data,
                'creador_por': oportunidad_data['creador_por']
            }

            # Adjuntar archivo multimedia si se subió
            if form.archivo_multimedia.data:
                archivo = form.archivo_multimedia.data
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static/uploads', filename)
                archivo.save(filepath)
                json_data['archivo_multimedia'] = filename
            else:
                json_data['archivo_multimedia'] = oportunidad_data.get('archivo_multimedia')

            # Actualizar en la API
            response = client.auto_update_data(
                where_condition=f"codigo_oportunidad = {codigo_oportunidad}",
                json_data=json_data
            )

            if response:
                mensaje_experto = getattr(form, 'mensaje_experto', None)
                mensaje = mensaje_experto.data if mensaje_experto else None
                print(f"mensaje_experto recibido: {mensaje}")

                if is_experto and mensaje:
                    create_notification(
                        experto_email=user_email,
                        tipo_entidad='oportunidad',
                        entidad_titulo=form.titulo.data,
                        accion='editar',
                        usuario_email=oportunidad_data['creador_por'],
                        mensaje_experto=mensaje
                    )

                flash('Oportunidad actualizada con éxito.', 'success')
                return redirect(url_for('list_oportunidad'))
            else:
                flash('No hubo cambios en los datos.', 'info')

        except Exception as e:
            flash(f'Error al actualizar la oportunidad: {e}', 'danger')
    else:
        flash('Formulario inválido. Por favor, revisa los datos ingresados.', 'warning')

...

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para manejar las sesiones y flashes

@app.route('/confirmar_oportunidad/<int:codigo_oportunidad>', methods=['GET', 'POST'])
def confirmar_oportunidad(codigo_oportunidad):
    print("Inicio de la función confirmar_oportunidad")

    # Obtener el correo electrónico del usuario autenticado
    user_email = session.get('user_email')
    print(f"Correo electrónico del usuario: {user_email}")
    if not user_email:
        flash('No has iniciado sesión. Por favor, inicia sesión para confirmar la oportunidad.', 'error')
        return redirect('/login')  # Redirige a la página de login

    # Verificar si el usuario es experto
    try:
        print("Consultando datos del perfil del usuario...")
        api_client_perfil = APIClient(table_name="perfil")
        perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
        print(f"Datos del perfil obtenidos: {perfil_data}")
    except Exception as e:
        print(f"Error al consultar perfil: {e}")
        perfil_data = []

    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')
        is_experto = (rol_usuario == 'Experto')
        print(f"Rol del usuario: {rol_usuario}, ¿Es experto?: {is_experto}")
    else:
        is_experto = False

    # Llamada a la API para obtener los datos de la oportunidad
    try:
        print(f"Consultando oportunidad con código: {codigo_oportunidad}...")
        client = APIClient('oportunidad')
        oportunidad = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")
        print(f"Oportunidad obtenida: {oportunidad}")
    except Exception as e:
        print(f"Error al consultar la oportunidad: {e}")
        oportunidad = []

    if not oportunidad:
        flash('Oportunidad no encontrada.', 'error')
        return redirect('/oportunidades')  # Redirige a la lista de oportunidades

    oportunidad_data = oportunidad[0]
    print(f"Datos de la oportunidad: {oportunidad_data}")

    # Verificación de creador_por
    usuario_email = oportunidad_data.get('creador_por')
    if not usuario_email:
        flash('No se encontró el correo del usuario asociado a esta oportunidad.', 'error')
        return redirect('/oportunidades')

    # Procesamiento del formulario
    if request.method == 'POST' and 'confirmar' in request.form:
        print("Formulario POST recibido, procesando confirmación de la oportunidad...")
        try:
            # Cambiar el estado de la oportunidad a True
            json_data = {'estado': True}
            print(f"Actualizando estado de la oportunidad a: {json_data}")
            response = client.auto_update_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}", json_data=json_data)
            print(f"Respuesta de actualización: {response}")

            if response:
                # Transferir oportunidad a proyecto si se confirma
                print("Confirmación exitosa, transfiriendo oportunidad a proyecto...")
                proyecto_client = APIClient('proyecto')
                fecha_aprobacion = django_timezone.now().isoformat()

                proyecto_data = {
                    "tipo_origen": "oportunidad",
                    "id_origen": codigo_oportunidad,
                    "titulo": oportunidad_data.get('titulo'),
                    "descripcion": oportunidad_data.get('descripcion'),
                    "fecha_creacion": oportunidad_data.get('fecha_creacion'),
                    "palabras_claves": oportunidad_data.get('palabras_claves'),
                    "recursos_requeridos": oportunidad_data.get('recursos_requeridos'),
                    "archivo_multimedia": oportunidad_data.get('archivo_multimedia'),
                    "creador_por": oportunidad_data.get('creador_por'),
                    "id_tipo_innovacion": oportunidad_data.get('id_tipo_innovacion'),
                    "id_foco_innovacion": oportunidad_data.get('id_foco_innovacion'),
                    "estado": True,
                    "fecha_aprobacion": fecha_aprobacion,
                    "aprobado_por": user_email,
                }
                print(f"Datos del proyecto a insertar: {proyecto_data}")

                proyecto_response = proyecto_client.insert_data(json_data=proyecto_data)
                print(f"Respuesta de inserción de proyecto: {proyecto_response}")

                if proyecto_response:
                    flash('La oportunidad ha sido confirmada y transferida a proyecto exitosamente.', 'success')
                    return redirect('/oportunidades')  # Redirige a la lista de oportunidades
                else:
                    flash('La oportunidad fue confirmada, pero hubo un error al crear el proyecto.', 'error')

            else:
                flash('Hubo un error al confirmar la oportunidad.', 'error')

        except Exception as e:
            print(f"Excepción durante la confirmación de la oportunidad: {e}")
            flash(f'Error al confirmar la oportunidad: {e}', 'error')

    return render_template('confirmar_oportunidades.html', oportunidad=oportunidad_data, is_experto=is_experto)


if __name__ == '__main__':
    app.run(debug=True)

                  
