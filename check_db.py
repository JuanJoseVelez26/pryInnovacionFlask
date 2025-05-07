from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2

# Configuración de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postres@localhost:5432/bd_Innovacion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

def check_and_clean_transactions():
    """Verifica y limpia transacciones pendientes"""
    try:
        # Conexión directa con psycopg2 para tener más control
        conn = psycopg2.connect(
            dbname="bd_Innovacion",
            user="postgres",
            password="Postres",
            host="localhost",
            port="5432"
        )
        
        # Hacer la conexión autocommit para evitar transacciones pendientes
        conn.set_session(autocommit=True)
        
        with conn.cursor() as cur:
            # Verificar transacciones activas
            cur.execute("""
                SELECT pid, usename, application_name, state, query_start, state_change
                FROM pg_stat_activity 
                WHERE state = 'idle in transaction'
            """)
            
            idle_transactions = cur.fetchall()
            if idle_transactions:
                print("Transacciones pendientes encontradas:")
                for trans in idle_transactions:
                    print(f"PID: {trans[0]}, Usuario: {trans[1]}, Estado: {trans[3]}")
                    
                    # Terminar transacciones idle
                    cur.execute(f"SELECT pg_terminate_backend({trans[0]})")
                
                print("Transacciones pendientes terminadas")
            else:
                print("No hay transacciones pendientes")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error al verificar transacciones: {str(e)}")
        return False

if __name__ == '__main__':
    print("Verificando estado de la base de datos...")
    check_and_clean_transactions()
    print("Verificación completada.") 