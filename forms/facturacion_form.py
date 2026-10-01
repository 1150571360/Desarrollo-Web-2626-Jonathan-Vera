from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Regexp, NumberRange, Optional


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

    mesa = IntegerField(
        "Mesa",
        validators=[Optional(), NumberRange(min=1, max=100, message="Ingrese un número válido.")]
    )

    fecha_hora = DateTimeLocalField(
        "Fecha y hora",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="La fecha y hora son obligatorias.")]
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

    submit = SubmitField("Generar factura")