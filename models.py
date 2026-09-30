from flask_login import UserMixin
from conexion.conexion import get_conexion


class Usuario(UserMixin):
    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password


def obtener_usuario_por_id(user_id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    if fila:
        return Usuario(fila['id'], fila['usuario'], fila['password'])
    return None


def obtener_usuario_por_nombre(nombre_usuario):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', (nombre_usuario,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    if fila:
        return Usuario(fila['id'], fila['usuario'], fila['password'])
    return None