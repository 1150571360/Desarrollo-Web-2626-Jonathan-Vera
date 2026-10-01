import io
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, abort, request, flash, send_file
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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
            'INSERT INTO productos (nombre, categoria, precio, unidades, estado, descripcion, proveedor_id) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (form.nombre.data, form.categoria.data, form.precio.data, form.unidades.data,
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
            'UPDATE productos SET nombre=%s, categoria=%s, precio=%s, unidades=%s, estado=%s, '
            'descripcion=%s, proveedor_id=%s WHERE id=%s',
            (form.nombre.data, form.categoria.data, form.precio.data, form.unidades.data,
             form.estado.data, form.descripcion.data, proveedor_id, id)
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
            'INSERT INTO clientes (nombre, cedula, correo, telefono, tipo, canal_preferido, compras) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (form.nombre.data, form.cedula.data, form.correo.data, form.telefono.data,
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
            'UPDATE clientes SET nombre=%s, cedula=%s, correo=%s, telefono=%s, tipo=%s, '
            'canal_preferido=%s, compras=%s WHERE id=%s',
            (form.nombre.data, form.cedula.data, form.correo.data, form.telefono.data, form.tipo.data,
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
# MODULO FACTURACION - MySQL - múltiples productos por factura + PDF estilo SRI
# ---------------------------------------------------------------------------

IVA_PORCENTAJE = 0.15


def obtener_cliente_por_id(cliente_id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    return fila


def obtener_productos_disponibles():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, precio, unidades FROM productos WHERE estado = 'Disponible' AND unidades > 0 ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas

@app.route('/facturacion')
def facturacion():
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM facturas ORDER BY id DESC')
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
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')

        lineas_validas = [
            (int(pid), int(cant)) for pid, cant in zip(producto_ids, cantidades)
            if pid and int(cant or 0) > 0
        ]

        if not lineas_validas:
            flash('Debe agregar al menos un producto a la factura.', 'danger')
        else:
            cliente = obtener_cliente_por_id(form.cliente_id.data)

            conn = get_conexion()
            cursor = conn.cursor(dictionary=True)

            # Primero validamos que haya stock suficiente para TODO antes de guardar nada
            subtotal = 0.0
            detalles = []
            error_stock = None
            for producto_id, cantidad in lineas_validas:
                cursor.execute('SELECT nombre, precio, unidades FROM productos WHERE id = %s', (producto_id,))
                producto = cursor.fetchone()
                if producto:
                    if cantidad > producto['unidades']:
                        error_stock = f"No hay suficiente stock de '{producto['nombre']}' (disponible: {producto['unidades']})."
                        break
                    subtotal_linea = float(producto['precio']) * cantidad
                    subtotal += subtotal_linea
                    detalles.append((producto_id, producto['nombre'], producto['precio'], cantidad, subtotal_linea))

            if error_stock:
                flash(error_stock, 'danger')
                cursor.close()
                conn.close()
                return render_template(
                    'formulario_facturacion.html',
                    form=form, modo='nuevo',
                    productos_disponibles=obtener_productos_disponibles(),
                    lineas_existentes=[]
                )

            iva = round(subtotal * IVA_PORCENTAJE, 2)
            total = round(subtotal + iva, 2)

            cursor.execute(
                'INSERT INTO facturas (numero, cliente_id, cliente_nombre, cliente_cedula, mesa, '
                'fecha_hora, metodo_pago, estado, subtotal, iva, total) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (form.numero.data, cliente['id'], cliente['nombre'], cliente.get('cedula'),
                 form.mesa.data, form.fecha_hora.data, form.metodo_pago.data, form.estado.data,
                 round(subtotal, 2), iva, total)
            )
            factura_id = cursor.lastrowid

            for producto_id, nombre, precio, cantidad, subtotal_linea in detalles:
                cursor.execute(
                    'INSERT INTO factura_detalle (factura_id, producto_id, producto_nombre, '
                    'precio_unitario, cantidad, subtotal_linea) VALUES (%s, %s, %s, %s, %s, %s)',
                    (factura_id, producto_id, nombre, precio, cantidad, subtotal_linea)
                )
                # Resta el stock vendido
                cursor.execute(
                    'UPDATE productos SET unidades = unidades - %s WHERE id = %s',
                    (cantidad, producto_id)
                )

            conn.commit()
            cursor.close()
            conn.close()

            flash('Factura registrada correctamente.', 'success')
            return redirect(url_for('facturacion'))

    return render_template(
        'formulario_facturacion.html',
        form=form, modo='nuevo',
        productos_disponibles=obtener_productos_disponibles(),
        lineas_existentes=[]
    )

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

    if request.method == 'GET':
        form.cliente_id.data = factura['cliente_id']

    if form.validate_on_submit():
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')

        lineas_validas = [
            (int(pid), int(cant)) for pid, cant in zip(producto_ids, cantidades)
            if pid and int(cant or 0) > 0
        ]

        if not lineas_validas:
            flash('Debe agregar al menos un producto a la factura.', 'danger')
        else:
            cliente = obtener_cliente_por_id(form.cliente_id.data)

            conn = get_conexion()
            cursor = conn.cursor(dictionary=True)

            subtotal = 0.0
            detalles = []
            for producto_id, cantidad in lineas_validas:
                cursor.execute('SELECT nombre, precio FROM productos WHERE id = %s', (producto_id,))
                producto = cursor.fetchone()
                if producto:
                    subtotal_linea = float(producto['precio']) * cantidad
                    subtotal += subtotal_linea
                    detalles.append((producto_id, producto['nombre'], producto['precio'], cantidad, subtotal_linea))

            iva = round(subtotal * IVA_PORCENTAJE, 2)
            total = round(subtotal + iva, 2)

            cursor.execute(
                'UPDATE facturas SET numero=%s, cliente_id=%s, cliente_nombre=%s, cliente_cedula=%s, '
                'mesa=%s, fecha_hora=%s, metodo_pago=%s, estado=%s, subtotal=%s, iva=%s, total=%s '
                'WHERE id=%s',
                (form.numero.data, cliente['id'], cliente['nombre'], cliente.get('cedula'),
                 form.mesa.data, form.fecha_hora.data, form.metodo_pago.data, form.estado.data,
                 round(subtotal, 2), iva, total, id)
            )

            cursor.execute('DELETE FROM factura_detalle WHERE factura_id = %s', (id,))
            for producto_id, nombre, precio, cantidad, subtotal_linea in detalles:
                cursor.execute(
                    'INSERT INTO factura_detalle (factura_id, producto_id, producto_nombre, '
                    'precio_unitario, cantidad, subtotal_linea) VALUES (%s, %s, %s, %s, %s, %s)',
                    (id, producto_id, nombre, precio, cantidad, subtotal_linea)
                )

            conn.commit()
            cursor.close()
            conn.close()

            flash('Factura actualizada correctamente.', 'success')
            return redirect(url_for('facturacion'))

    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT producto_id, cantidad FROM factura_detalle WHERE factura_id = %s', (id,))
    lineas_existentes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'formulario_facturacion.html',
        form=form, modo='editar', id=id,
        productos_disponibles=obtener_productos_disponibles(),
        lineas_existentes=lineas_existentes
    )


@app.route('/facturacion/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_facturacion(id):
    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)

    # Devuelve el stock de cada producto antes de borrar la factura
    cursor.execute('SELECT producto_id, cantidad FROM factura_detalle WHERE factura_id = %s', (id,))
    detalles = cursor.fetchall()
    for d in detalles:
        if d['producto_id']:
            cursor.execute('UPDATE productos SET unidades = unidades + %s WHERE id = %s', (d['cantidad'], d['producto_id']))

    cursor.execute('DELETE FROM facturas WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Factura eliminada (stock restaurado).', 'info')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/pdf/<int:id>')
@login_required
def factura_pdf(id):
    """Genera la factura en PDF con formato similar al SRI (Ecuador)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    conn = get_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM facturas WHERE id = %s', (id,))
    factura = cursor.fetchone()
    cursor.execute('SELECT * FROM factura_detalle WHERE factura_id = %s', (id,))
    detalle = cursor.fetchall()
    cursor.close()
    conn.close()

    if factura is None:
        abort(404)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    estilos = getSampleStyleSheet()
    elementos = []

    estilo_emisor = estilos['Normal']
    tabla_encabezado = Table([
        [
            Paragraph("<b>TECNO PLUS</b><br/>Venta de equipos y servicios tecnológicos<br/>"
                      "Av. Principal y Secundaria, Quito - Ecuador<br/>"
                      "Teléfono: 02-2345678<br/>RUC: 1792345678001", estilo_emisor),
            Paragraph(f"<b>FACTURA</b><br/>N°: {factura['numero']}<br/>"
                      f"Fecha emisión: {factura['fecha_hora'].strftime('%d/%m/%Y %H:%M')}<br/>"
                      f"Ambiente: PRUEBAS<br/>Autorización: {factura['numero'].replace('-', '')}0001",
                      estilo_emisor),
        ]
    ], colWidths=[9 * cm, 9 * cm])
    tabla_encabezado.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_encabezado)
    elementos.append(Spacer(1, 0.5 * cm))

    tabla_cliente = Table([
        [Paragraph(f"<b>Razón social / Nombre:</b> {factura['cliente_nombre']}", estilo_emisor)],
        [Paragraph(f"<b>Identificación:</b> {factura['cliente_cedula'] or 'N/A'}", estilo_emisor)],
        [Paragraph(f"<b>Método de pago:</b> {factura['metodo_pago']} &nbsp;&nbsp; "
                   f"<b>Mesa:</b> {factura['mesa'] or 'N/A'} &nbsp;&nbsp; "
                   f"<b>Estado:</b> {factura['estado']}", estilo_emisor)],
    ], colWidths=[18 * cm])
    tabla_cliente.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabla_cliente)
    elementos.append(Spacer(1, 0.5 * cm))

    datos_tabla = [["Cant.", "Descripción", "P. Unitario", "Subtotal"]]
    for linea in detalle:
        datos_tabla.append([
            str(linea['cantidad']),
            linea['producto_nombre'],
            f"${float(linea['precio_unitario']):.2f}",
            f"${float(linea['subtotal_linea']):.2f}",
        ])

    tabla_detalle = Table(datos_tabla, colWidths=[2 * cm, 9 * cm, 3.5 * cm, 3.5 * cm])
    tabla_detalle.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2744')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla_detalle)
    elementos.append(Spacer(1, 0.4 * cm))

    tabla_totales = Table([
        ["Subtotal:", f"${float(factura['subtotal']):.2f}"],
        ["IVA (15%):", f"${float(factura['iva']):.2f}"],
        ["TOTAL A PAGAR:", f"${float(factura['total']):.2f}"],
    ], colWidths=[14.5 * cm, 3.5 * cm])
    tabla_totales.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
    ]))
    elementos.append(tabla_totales)
    elementos.append(Spacer(1, 1 * cm))
    elementos.append(Paragraph(
        "<i>Este documento es una representación impresa de uso interno, generada por el sistema Tecno Plus.</i>",
        estilos['Normal']
    ))

    doc.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"factura_{factura['numero']}.pdf"
    )


if __name__ == '__main__':
    app.run(debug=True)