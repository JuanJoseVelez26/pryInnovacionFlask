from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Definir la URL base de la API
API_BASE_URL = "http://190.217.58.246:5186/api/sgv"

# Funciones para obtener datos desde la API
def obtener_focos_innovacion():
    response = requests.get(f"{API_BASE_URL}/foco_innovacion")
    return response.json() if response.status_code == 200 else []

def obtener_tipos_innovacion():
    response = requests.get(f"{API_BASE_URL}/tipo_innovacion")
    return response.json() if response.status_code == 200 else []

def obtener_ideas(filtro_tipo=None, filtro_foco=None, filtro_estado=None):
    params = {}
    if filtro_tipo:
        params["tipo_innovacion"] = filtro_tipo
    if filtro_foco:
        params["foco_innovacion"] = filtro_foco
    if filtro_estado is not None:
        params["estado"] = filtro_estado

    response = requests.get(f"{API_BASE_URL}/ideas", params=params)
    return response.json() if response.status_code == 200 else []

# Página de inicio
@app.route('/')
def home():
    return "Hola, Flask está funcionando!"

# Endpoint para mostrar la lista de ideas con filtros
@app.route('/ideas', methods=['GET'])
def lista_ideas():
    filtro_tipo = request.args.get('tipo_innovacion')
    filtro_foco = request.args.get('foco_innovacion')
    filtro_estado = request.args.get('estado')

    ideas = obtener_ideas(filtro_tipo, filtro_foco, filtro_estado)
    tipos = obtener_tipos_innovacion()
    focos = obtener_focos_innovacion()

    return render_template(
        "list1.html",  # Cambié el nombre de la plantilla aquí
        ideas=ideas,
        tipos=tipos,
        focos=focos,
        selected_tipo=filtro_tipo,
        selected_foco=filtro_foco,
        selected_estado=filtro_estado
    )

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

