from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class ProveedorForm(FlaskForm):
    """Formulario para registrar/editar un proveedor de equipos y componentes."""

    empresa = StringField(
        "Nombre de la empresa",
        validators=[DataRequired(message="El nombre de la empresa es obligatorio."),
                    Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres.")]
    )

    producto = StringField(
        "Producto que provee",
        validators=[DataRequired(message="El producto es obligatorio."),
                    Length(min=3, max=150, message="Debe tener entre 3 y 150 caracteres.")]
    )

    categoria = SelectField(
        "Categoría",
        choices=[
            ("Computadoras", "Computadoras"),
            ("Accesorios", "Accesorios"),
            ("Teléfonos", "Teléfonos"),
            ("Software", "Software"),
        ],
        validators=[DataRequired(message="Seleccione una categoría.")]
    )

    contacto = StringField(
        "Teléfono de contacto",
        validators=[DataRequired(message="El contacto es obligatorio."),
                    Regexp(r"^09\d{8}$", message="Ingrese un teléfono válido (10 dígitos, inicia con 09).")]
    )

    frecuencia = SelectField(
        "Frecuencia de entrega",
        choices=[("Semanal", "Semanal"), ("Quincenal", "Quincenal"), ("Mensual", "Mensual")],
        validators=[DataRequired(message="Seleccione la frecuencia de entrega.")]
    )

    submit = SubmitField("Guardar proveedor")
