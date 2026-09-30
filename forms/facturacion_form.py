from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


class FacturacionForm(FlaskForm):
    numero = StringField(
        "N° de factura",
        validators=[DataRequired(message="El número de factura es obligatorio."),
                    Regexp(r"^\d{3}-\d{3}-\d{9}$", message="Formato esperado: 001-001-000000123.")]
    )

    cliente_id = SelectField(
        "Cliente",
        coerce=int,
        validators=[DataRequired(message="Seleccione un cliente.")]
    )

    sucursal = IntegerField(
        "N° de sucursal",
        validators=[DataRequired(message="El número de sucursal es obligatorio."),
                    NumberRange(min=1, max=20, message="Ingrese una sucursal entre 1 y 20.")]
    )

    productos = TextAreaField(
        "Productos/servicios vendidos (separados por coma)",
        validators=[DataRequired(message="Debe indicar al menos un producto."),
                    Length(min=3, max=300, message="Debe tener entre 3 y 300 caracteres.")]
    )

    subtotal = FloatField(
        "Subtotal ($)",
        validators=[DataRequired(message="El subtotal es obligatorio."),
                    NumberRange(min=0.01, max=5000, message="El subtotal debe estar entre 0.01 y 5000.")]
    )

    metodo_pago = SelectField(
        "Método de pago",
        choices=[("Efectivo", "Efectivo"), ("Tarjeta", "Tarjeta"), ("Transferencia", "Transferencia")],
        validators=[DataRequired(message="Seleccione el método de pago.")]
    )

    estado = SelectField(
        "Estado",
        choices=[("Pagada", "Pagada"), ("Pendiente", "Pendiente")],
        validators=[DataRequired(message="Seleccione el estado.")]
    )

    fecha = StringField(
        "Fecha (dd/mm/aaaa)",
        validators=[DataRequired(message="La fecha es obligatoria."),
                    Regexp(r"^\d{2}/\d{2}/\d{4}$", message="Formato esperado: dd/mm/aaaa.")]
    )

    submit = SubmitField("Guardar factura")