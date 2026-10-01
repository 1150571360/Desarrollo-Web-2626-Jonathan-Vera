from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    """Formulario para registrar/editar un producto o servicio del catálogo."""

    nombre = StringField(
        "Nombre del producto/servicio",
        validators=[DataRequired(message="El nombre es obligatorio."),
                    Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres.")]
    )

    categoria = SelectField(
        "Categoría",
        choices=[
            ("Computadoras", "Computadoras"),
            ("Accesorios", "Accesorios"),
            ("Teléfonos", "Teléfonos"),
            ("Soporte Técnico", "Soporte Técnico"),
            ("Instalación de Software", "Instalación de Software"),
        ],
        validators=[DataRequired(message="Seleccione una categoría.")]
    )

    proveedor_id = SelectField(
        "Proveedor (opcional)",
        coerce=int,
        validators=[Optional()]
    )

    precio = FloatField(
        "Precio ($)",
        validators=[DataRequired(message="El precio es obligatorio."),
                    NumberRange(min=0.01, max=3000, message="El precio debe estar entre 0.01 y 3000.")]
    )

    unidades = IntegerField(
        "Unidades disponibles (stock)",
        validators=[DataRequired(message="Indique las unidades disponibles."),
                    NumberRange(min=0, max=100000, message="Debe ser un número entre 0 y 100000.")]
    )

    estado = SelectField(
        "Estado",
        choices=[("Disponible", "Disponible"), ("Agotado", "Agotado")],
        validators=[DataRequired(message="Seleccione el estado.")]
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[DataRequired(message="La descripción es obligatoria."),
                    Length(min=10, max=300, message="Debe tener entre 10 y 300 caracteres.")]
    )

    submit = SubmitField("Guardar producto")