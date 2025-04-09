from django.http import HttpResponse
from ..models import APIClient
from django.shortcuts import redirect, render


def dashboard_view(request):
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')
    
    # Instancia del APIClient para las tablas 'idea' , 'oportunidad', 'soluciones'
    ideas_client = APIClient(table_name="idea")
    oportunidades_client = APIClient(table_name="oportunidad")
    solucion_client = APIClient(table_name="solucion")
    usuario_client = APIClient(table_name="usuario")

    try:
        # Obtener los datos de las tablas
        ideas_data = ideas_client.get_data(select_columns="titulo")
        oportunidades_data = oportunidades_client.get_data(select_columns="titulo")
        solucion_data = solucion_client.get_data(select_columns="titulo")
        usuario_data = usuario_client.get_data(select_columns="email")

        # Calcular la cantidad de ideas y oportunidades
        ideas_count = len(ideas_data) if ideas_data else 0
        oportunidades_count = len(oportunidades_data) if oportunidades_data else 0
        solucion_count = len(solucion_data) if solucion_data else 0
        usuario_count = len(usuario_data) if usuario_data else 0

        # Calcular el porcentaje de oportunidades respecto a ideas
        if ideas_count > 0:
            oportunidades_percentage = (oportunidades_count / ideas_count) * 100
        else:
            oportunidades_percentage = 0

    except Exception as e:
        # Manejo de errores
        print(f"Error al obtener los datos: {e}")
        ideas_count = 0
        oportunidades_count = 0
        solucion_count = 0
        usuario_count = 0
        oportunidades_percentage = 0

    # Pasar los valores al contexto
    context = {
        'ideas_count': ideas_count,
        'oportunidades_count': oportunidades_count,
        'solucion_count': solucion_count,
        'usuario_count': usuario_count,
        # 'oportunidades_percentage': oportunidades_percentage,
    }

    return render(request, 'dashboard.html', context)
