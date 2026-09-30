import os
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------------------------
# Conexion a MySQL LOCAL (XAMPP / WAMP / MySQL Server instalado en tu PC)
# Ajusta host/user/password si tu instalacion es distinta.
# Por defecto, XAMPP usa: user='root', password='' (vacia)
# ---------------------------------------------------------------------------

CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '3306'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'tecnoplus_db'),
}


def get_conexion():
    """Devuelve una conexion a MySQL. Los cursores se piden con
    dictionary=True para acceder a las columnas por nombre (fila['nombre'])."""
    try:
        conn = mysql.connector.connect(**CONFIG)
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        raise