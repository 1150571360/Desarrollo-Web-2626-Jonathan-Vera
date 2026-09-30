import io
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, abort, request, flash, send_file
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.login_form import LoginForm
from forms.usuario_form import RegistroForm

from conexion.conexion import get_conexion
from models import obtener_usuario_por_id, obtener_usuario_por_nombre

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tecno-plus-tienda-tecnologica-clave-secreta-2026'
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return obtener_usuario_por_id(user_id)


# ---------------------------------------------------------------------------
# Utilidades para poblar los <select> con datos reales (relaciones FK)
# ---------------------------------------------------------------------------

def obtener_choices_proveedores():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, empresa FROM proveedores ORDER BY empresa')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [(0, '-- Sin proveedor --')] + [(f['id'], f['empresa']) for f in filas]


def obtener_choices_clientes():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nombre FROM clientes ORDER BY nombre')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [(f['id'], f['nombre']) for f in filas]


# RUTA PRINCIPAL
@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------------------------
# AUTENTICACION (registro / login / logout) - basada en MySQL
# ---------------------------------------------------------------------------

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        if obtener_usuario_por_nombre(form.usuario.data):
            flash('Ese nombre de usuario ya existe, elige otro.', 'danger')
        else:
            password_hash = generate_password_hash(form.password.data)
            conn = get_conexion()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO usuarios (usuario, password) VALUES (%s, %s)',
                (form.usuario.data, password_hash)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Usuario registrado correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    return render_template('registro.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = obtener_usuario_por_nombre(form.usuario.data)
        if usuario and check_password_hash(usuario.password, form.contrasena.data):
            login_user(usuario)
            return redirect(url_for('panel'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))


@app.route('/panel')
@login_required
def panel():
    return render_template('panel.html')


# ---------------------------------------------------------------------------
# MODULO PRODUCTOS (Catálogo tecnológico) - MySQL
# ---------------------------------------------------------------------------

@app.route('/productos')
def productos():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, pr.empresa AS proveedor_nombre
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
        ORDER BY p.categoria, p.nombre
    ''')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    categorias = sorted(set(f['categoria'] for f in filas))
    return render_template('productos.html', productos=filas, categorias=categorias)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    form.proveedor_id.choices = obtener_choices_proveedores()
    if form.validate_on_submit():
        proveedor_id = form.proveedor_id.data if form.proveedor_id.data != 0 else None
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO productos (nombre, categoria, precio, estado, descripcion, proveedor_id) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (form.nombre.data, form.categoria.data, form.precio.data,
             form.estado.data, form.descripcion.data, proveedor_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Producto registrado correctamente.', 'success')
        return redirect(url_for('productos'))
    return render_template('formulario_productos.html', form=form, modo='nuevo')


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    if producto is None:
        abort(404)

    form = ProductoForm(data=producto) if request.method == 'GET' else ProductoForm()
    form.proveedor_id.choices = obtener_choices_proveedores()

    if form.validate_on_submit():
        proveedor_id = form.proveedor_id.data if form.proveedor_id.data != 0 else None
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE productos SET nombre=%s, categoria=%s, precio=%s, estado=%s, '
            'descripcion=%s, proveedor_id=%s WHERE id=%s',
            (form.nombre.data, form.categoria.data, form.precio.data, form.estado.data,
             form.descripcion.data, proveedor_id, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('productos'))

    return render_template('formulario_productos.html', form=form, modo='editar', id=id)


@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Producto eliminado.', 'info')
    return redirect(url_for('productos'))


# ---------------------------------------------------------------------------
# MODULO CLIENTES - MySQL
# ---------------------------------------------------------------------------

@app.route('/clientes')
def clientes():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=filas)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO clientes (nombre, correo, telefono, tipo, canal_preferido, compras) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (form.nombre.data, form.correo.data, form.telefono.data,
             form.tipo.data, form.canal_preferido.data, form.compras.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form, modo='nuevo')


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    if cliente is None:
        abort(404)

    form = ClienteForm(data=cliente) if request.method == 'GET' else ClienteForm()

    if form.validate_on_submit():
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE clientes SET nombre=%s, correo=%s, telefono=%s, tipo=%s, '
            'canal_preferido=%s, compras=%s WHERE id=%s',
            (form.nombre.data, form.correo.data, form.telefono.data, form.tipo.data,
             form.canal_preferido.data, form.compras.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Cliente actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))

    return render_template('formulario_cliente.html', form=form, modo='editar', id=id)


@app.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Cliente eliminado.', 'info')
    return redirect(url_for('clientes'))


# ---------------------------------------------------------------------------
# MODULO PROVEEDORES - MySQL
# ---------------------------------------------------------------------------

@app.route('/proveedores')
def proveedores():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM proveedores ORDER BY empresa')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=filas)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO proveedores (empresa, producto, categoria, contacto, frecuencia) '
            'VALUES (%s, %s, %s, %s, %s)',
            (form.empresa.data, form.producto.data, form.categoria.data,
             form.contacto.data, form.frecuencia.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form, modo='nuevo')


@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM proveedores WHERE id = %s', (id,))
    proveedor = cursor.fetchone()
    cursor.close()
    conn.close()

    if proveedor is None:
        abort(404)

    form = ProveedorForm(data=proveedor) if request.method == 'GET' else ProveedorForm()

    if form.validate_on_submit():
        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE proveedores SET empresa=%s, producto=%s, categoria=%s, contacto=%s, '
            'frecuencia=%s WHERE id=%s',
            (form.empresa.data, form.producto.data, form.categoria.data,
             form.contacto.data, form.frecuencia.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Proveedor actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form, modo='editar', id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_proveedor(id):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedores WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Proveedor eliminado.', 'info')
    return redirect(url_for('proveedores'))


# ---------------------------------------------------------------------------
# MODULO FACTURACION - MySQL - JOIN con clientes + PDF con IVA 15%
# ---------------------------------------------------------------------------

IVA_PORCENTAJE = 0.15


@app.route('/facturacion')
def facturacion():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT f.*, c.nombre AS cliente_nombre
        FROM facturas f
        LEFT JOIN clientes c ON f.cliente_id = c.id
        ORDER BY f.id DESC
    ''')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('facturacion.html', facturas=filas)


@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_facturacion():
    form = FacturacionForm()
    form.cliente_id.choices = obtener_choices_clientes()
    if form.validate_on_submit():
        subtotal = form.subtotal.data
        iva = round(subtotal * IVA_PORCENTAJE, 2)
        total = round(subtotal + iva, 2)

        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO facturas (numero, cliente_id, sucursal, productos, subtotal, iva, total, '
            'metodo_pago, estado, fecha) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (form.numero.data, form.cliente_id.data, form.sucursal.data, form.productos.data,
             subtotal, iva, total, form.metodo_pago.data, form.estado.data, form.fecha.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Factura registrada correctamente.', 'success')
        return redirect(url_for('facturacion'))
    return render_template('formulario_facturacion.html', form=form, modo='nuevo')


@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_facturacion(id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM facturas WHERE id = %s', (id,))
    factura = cursor.fetchone()
    cursor.close()
    conn.close()

    if factura is None:
        abort(404)

    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()
    form.cliente_id.choices = obtener_choices_clientes()

    if form.validate_on_submit():
        subtotal = form.subtotal.data
        iva = round(subtotal * IVA_PORCENTAJE, 2)
        total = round(subtotal + iva, 2)

        conn = get_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE facturas SET numero=%s, cliente_id=%s, sucursal=%s, productos=%s, subtotal=%s, '
            'iva=%s, total=%s, metodo_pago=%s, estado=%s, fecha=%s WHERE id=%s',
            (form.numero.data, form.cliente_id.data, form.sucursal.data, form.productos.data,
             subtotal, iva, total, form.metodo_pago.data, form.estado.data, form.fecha.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Factura actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))

    return render_template('formulario_facturacion.html', form=form, modo='editar', id=id)


@app.route('/facturacion/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_facturacion(id):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM facturas WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Factura eliminada.', 'info')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/pdf/<int:id>')
@login_required
def factura_pdf(id):
    """Genera y descarga la factura en PDF, con el 15% de IVA."""
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, c.correo AS cliente_correo
        FROM facturas f
        LEFT JOIN clientes c ON f.cliente_id = c.id
        WHERE f.id = %s
    ''', (id,))
    factura = cursor.fetchone()
    cursor.close()
    conn.close()

    if factura is None:
        abort(404)

    buffer = io.BytesIO()
    doc = canvas.Canvas(buffer, pagesize=letter)
    ancho, alto = letter

    # Encabezado
    doc.setFont("Helvetica-Bold", 18)
    doc.drawString(2 * cm, alto - 2 * cm, "TecnoPlus")
    doc.setFont("Helvetica", 10)
    doc.drawString(2 * cm, alto - 2.6 * cm, "Factura de venta")
    doc.line(2 * cm, alto - 2.8 * cm, ancho - 2 * cm, alto - 2.8 * cm)

    # Datos de la factura
    y = alto - 3.5 * cm
    doc.setFont("Helvetica-Bold", 11)
    doc.drawString(2 * cm, y, f"N° Factura: {factura['numero']}")
    y -= 0.7 * cm
    doc.setFont("Helvetica", 11)
    doc.drawString(2 * cm, y, f"Cliente: {factura['cliente_nombre'] or 'N/A'}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"Correo: {factura.get('cliente_correo') or 'N/A'}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"Sucursal: {factura['sucursal']}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"Fecha: {factura['fecha']}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"Método de pago: {factura['metodo_pago']}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"Estado: {factura['estado']}")

    # Productos
    y -= 1 * cm
    doc.setFont("Helvetica-Bold", 11)
    doc.drawString(2 * cm, y, "Productos/servicios:")
    y -= 0.6 * cm
    doc.setFont("Helvetica", 10)
    for item in factura['productos'].split(','):
        doc.drawString(2.5 * cm, y, f"- {item.strip()}")
        y -= 0.5 * cm

    # Totales
    y -= 0.8 * cm
    doc.line(2 * cm, y, ancho - 2 * cm, y)
    y -= 0.7 * cm
    doc.setFont("Helvetica", 11)
    doc.drawString(2 * cm, y, f"Subtotal: ${float(factura['subtotal']):.2f}")
    y -= 0.6 * cm
    doc.drawString(2 * cm, y, f"IVA (15%): ${float(factura['iva']):.2f}")
    y -= 0.6 * cm
    doc.setFont("Helvetica-Bold", 13)
    doc.drawString(2 * cm, y, f"TOTAL: ${float(factura['total']):.2f}")

    doc.setFont("Helvetica-Oblique", 8)
    doc.drawString(2 * cm, 1.5 * cm, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    doc.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"factura_{factura['numero']}.pdf"
    )


if __name__ == '__main__':
    app.run(debug=True)