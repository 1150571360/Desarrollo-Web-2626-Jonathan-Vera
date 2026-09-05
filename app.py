from flask import Flask, render_template, redirect, url_for, abort, request, session
from flask_wtf.csrf import CSRFProtect
from functools import wraps

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.login_form import LoginForm

import sqlite3
import os

# Ruta absoluta a la base de datos, para que funcione sin importar desde dónde se ejecute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'tecnoplus.db')


def get_conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    return conn


def crear_tabla_productos():
    conn = get_conexion()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            estado TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


app = Flask(__name__)

# Clave secreta necesaria para el funcionamiento de Flask-WTF y la
# protección CSRF de los formularios.
app.config['SECRET_KEY'] = 'tecno-plus-tienda-tecnologica-clave-secreta-2026'

# Habilita la función csrf_token() en las plantillas, usada por los
# formularios de eliminar (botones que no usan una clase FlaskForm completa).
csrf = CSRFProtect(app)


# ---------------------------------------------------------------------------
# Autenticación simple (usuario y contraseña fijos, sin base de datos).
# ---------------------------------------------------------------------------

USUARIO_VALIDO = 'admin'
CONTRASENA_VALIDA = '1234'


def login_requerido(vista):
    """Decorador: bloquea el acceso a una ruta si no hay sesión iniciada."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not session.get('autenticado'):
            return redirect(url_for('login'))
        return vista(*args, **kwargs)
    return envoltura


# ---------------------------------------------------------------------------
# "Bases de datos" temporales en memoria (listas de Python).
# El módulo de productos ya usa SQLite (ver funciones get_conexion /
# crear_tabla_productos). Los demás módulos se migrarán progresivamente.
# ---------------------------------------------------------------------------

lista_clientes = [
    {"nombre": "Andrés Felipe Mora", "correo": "afmora@gmail.com",
     "telefono": "0991234567", "tipo": "Frecuente", "canal_preferido": "Tienda física", "compras": 12},
    {"nombre": "Valentina Suárez Toro", "correo": "vsuarez@gmail.com",
     "telefono": "0987654321", "tipo": "Nuevo", "canal_preferido": "En línea", "compras": 1},
    {"nombre": "Sebastián Ortiz Peña", "correo": "sortiz@gmail.com",
     "telefono": "0965432198", "tipo": "Frecuente", "canal_preferido": "En línea", "compras": 20},
    {"nombre": "Camila Rueda Zamora", "correo": "cruedaz@gmail.com",
     "telefono": "0978965412", "tipo": "Nuevo", "canal_preferido": "Tienda física", "compras": 3},
]

lista_proveedores = [
    {"empresa": "GlobalTech Imports S.A.", "producto": "Laptops y computadoras",
     "categoria": "Computadoras", "contacto": "0998765432", "frecuencia": "Mensual"},
    {"empresa": "CircuitoAndino Cía. Ltda.", "producto": "Teclados, mouse y audífonos",
     "categoria": "Accesorios", "contacto": "0987651234", "frecuencia": "Quincenal"},
    {"empresa": "MovilMax Distribuciones", "producto": "Teléfonos móviles",
     "categoria": "Teléfonos", "contacto": "0965478123", "frecuencia": "Semanal"},
    {"empresa": "CloudSoft Solutions", "producto": "Licencias de software",
     "categoria": "Software", "contacto": "0976543210", "frecuencia": "Mensual"},
]

lista_facturas = [
    {"numero": "001-001-000000123", "cliente": "Andrés Felipe Mora", "sucursal": 1,
     "productos": ["Laptop TecnoPlus Pro 14", "Mouse inalámbrico"],
     "subtotal": 850.00, "iva": 102.00, "total": 952.00,
     "metodo_pago": "Tarjeta", "estado": "Pagada", "fecha": "10/08/2026"},
    {"numero": "001-001-000000124", "cliente": "Valentina Suárez Toro", "sucursal": 2,
     "productos": ["Audífonos Bluetooth"],
     "subtotal": 45.00, "iva": 5.40, "total": 50.40,
     "metodo_pago": "Efectivo", "estado": "Pagada", "fecha": "11/08/2026"},
    {"numero": "001-001-000000125", "cliente": "Sebastián Ortiz Peña", "sucursal": 1,
     "productos": ["Smartphone Galaxy A55", "Cargador rápido 30W"],
     "subtotal": 420.00, "iva": 50.40, "total": 470.40,
     "metodo_pago": "Transferencia", "estado": "Pendiente", "fecha": "12/08/2026"},
]


# RUTA PRINCIPAL
@app.route('/')
def index():
    return render_template('index.html')


# INICIO DE SESION (acceso al sistema interno)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        if form.usuario.data == USUARIO_VALIDO and form.contrasena.data == CONTRASENA_VALIDA:
            session['usuario'] = form.usuario.data
            session['autenticado'] = True
            return redirect(url_for('panel'))
        else:
            error = 'Usuario o contraseña incorrectos.'
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# PANEL DEL SISTEMA (rutas internas: Clientes, Facturación, Productos, Proveedores)
@app.route('/panel')
@login_requerido
def panel():
    return render_template('panel.html')


# ---------------------------------------------------------------------------
# MODULO PRODUCTOS (Catálogo tecnológico) - Persistencia con SQLite
# ---------------------------------------------------------------------------

@app.route('/productos')
def productos():
    conn = get_conexion()
    filas = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()

    categorias = sorted(set(fila['categoria'] for fila in filas))
    return render_template('productos.html', productos=filas, categorias=categorias)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        conn = get_conexion()
        conn.execute(
            'INSERT INTO productos (nombre, categoria, precio, estado, descripcion) VALUES (?, ?, ?, ?, ?)',
            (form.nombre.data, form.categoria.data, form.precio.data, form.estado.data, form.descripcion.data)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))
    return render_template('formulario_productos.html', form=form, modo='nuevo')


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_producto(id):
    conn = get_conexion()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    conn.close()

    if producto is None:
        abort(404)

    if request.method == 'GET':
        form = ProductoForm(data=dict(producto))
    else:
        form = ProductoForm()

    if form.validate_on_submit():
        conn = get_conexion()
        conn.execute(
            'UPDATE productos SET nombre = ?, categoria = ?, precio = ?, estado = ?, descripcion = ? WHERE id = ?',
            (form.nombre.data, form.categoria.data, form.precio.data, form.estado.data, form.descripcion.data, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))

    return render_template('formulario_productos.html', form=form, modo='editar', id=id)


@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_producto(id):
    conn = get_conexion()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('productos'))


# ---------------------------------------------------------------------------
# MODULO CLIENTES (Compradores de la tienda)
# ---------------------------------------------------------------------------

@app.route('/clientes')
def clientes():
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        lista_clientes.append({
            "nombre": form.nombre.data,
            "correo": form.correo.data,
            "telefono": form.telefono.data,
            "tipo": form.tipo.data,
            "canal_preferido": form.canal_preferido.data,
            "compras": form.compras.data,
        })
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form)


# ---------------------------------------------------------------------------
# MODULO PROVEEDORES (Insumos y componentes tecnológicos)
# ---------------------------------------------------------------------------

@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        lista_proveedores.append({
            "empresa": form.empresa.data,
            "producto": form.producto.data,
            "categoria": form.categoria.data,
            "contacto": form.contacto.data,
            "frecuencia": form.frecuencia.data,
        })
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form)


# ---------------------------------------------------------------------------
# MODULO FACTURACION (Ventas y órdenes)
# ---------------------------------------------------------------------------

@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html', facturas=lista_facturas)


@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_requerido
def nueva_facturacion():
    form = FacturacionForm()
    if form.validate_on_submit():
        subtotal = form.subtotal.data
        iva = round(subtotal * 0.12, 2)
        total = round(subtotal + iva, 2)
        productos_lista = [p.strip() for p in form.productos.data.split(',') if p.strip()]
        lista_facturas.append({
            "numero": form.numero.data,
            "cliente": form.cliente.data,
            "sucursal": form.sucursal.data,
            "productos": productos_lista,
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "metodo_pago": form.metodo_pago.data,
            "estado": form.estado.data,
            "fecha": form.fecha.data,
        })
        return redirect(url_for('facturacion'))
    return render_template('formulario_facturacion.html', form=form)


crear_tabla_productos()

if __name__ == '__main__':
    app.run(debug=True)