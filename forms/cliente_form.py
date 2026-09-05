from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Regexp


class ClienteForm(FlaskForm):
    """Formulario para registrar/editar un cliente de Tecno Plus."""

    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="El nombre es obligatorio."),
                    Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres.")]
    )

    correo = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio."),
                    Email(message="Ingrese un correo electrónico válido.")]
    )

    telefono = StringField(
        "Teléfono",
        validators=[DataRequired(message="El teléfono es obligatorio."),
                    Regexp(r"^09\d{8}$", message="Ingrese un teléfono válido (10 dígitos, inicia con 09).")]
    )

    tipo = SelectField(
        "Tipo de cliente",
        choices=[("Nuevo", "Nuevo"), ("Frecuente", "Frecuente")],
        validators=[DataRequired(message="Seleccione el tipo de cliente.")]
    )

    canal_preferido = SelectField(
        "Canal preferido",
        choices=[
            ("Tienda física", "Tienda física"),
            ("En línea", "En línea"),
        ],
        validators=[DataRequired(message="Seleccione el canal preferido.")]
    )

    compras = IntegerField(
        "Número de compras",
        validators=[DataRequired(message="Este campo es obligatorio."),
                    NumberRange(min=0, max=999, message="Ingrese un número entre 0 y 999.")]
    )

    submit = SubmitField("Guardar cliente")
