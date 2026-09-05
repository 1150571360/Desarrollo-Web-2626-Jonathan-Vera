# Tecno Plus

Proyecto Integrador — Desarrollo de Aplicaciones Web
Aplicación Flask para la gestión de una tienda de tecnología (venta de computadoras,
accesorios, teléfonos y software, además de soporte técnico).

## Estructura del proyecto

```
tecnoplus/
├── app.py
├── requirements.txt
├── data/
│   └── tecnoplus.db          (se crea automáticamente al ejecutar la app)
├── forms/
│   ├── __init__.py
│   ├── producto_form.py
│   ├── cliente_form.py
│   ├── proveedor_form.py
│   └── facturacion_form.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── panel.html
│   ├── productos.html
│   ├── formulario_productos.html
│   ├── clientes.html
│   ├── formulario_cliente.html
│   ├── proveedores.html
│   ├── formulario_proveedor.html
│   ├── facturacion.html
│   ├── formulario_facturacion.html
│   └── components/
│       ├── navbar.html
│       └── footer.html
└── static/
    ├── css/style.css
    ├── js/script.js
    └── img/
```

## Cómo ejecutar el proyecto en Visual Studio Code

1. Descomprime este archivo y abre la carpeta `tecnoplus` en VS Code.
2. Abre una terminal dentro de VS Code (Terminal → Nueva terminal).
3. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Ejecuta la aplicación:

   ```bash
   python app.py
   ```

6. Abre el navegador en: http://127.0.0.1:5000

## Módulos incluidos

- **Productos**: catálogo con persistencia real en SQLite (`data/tecnoplus.db`).
  Incluye alta, edición y eliminación (INSERT / UPDATE / DELETE / SELECT).
- **Clientes**: gestión de compradores (datos en memoria, con formulario validado).
- **Proveedores**: gestión de proveedores de equipos y componentes (datos en memoria).
- **Facturación**: registro de ventas con cálculo automático de IVA (12%) y total.
- **Login / Panel**: acceso demostrativo al sistema interno.

## Tecnologías utilizadas

- Flask
- Jinja2 (herencia de plantillas, `{% for %}`, `{% if %}`, filtros, `{% include %}`)
- Flask-WTF / WTForms (validación de formularios y protección CSRF)
- SQLite (persistencia local del módulo de Productos)
- Bootstrap 5 + Bootstrap Icons (diseño responsive, paleta azul tecnológica)
