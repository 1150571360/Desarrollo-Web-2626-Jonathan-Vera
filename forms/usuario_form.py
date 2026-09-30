from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistroForm(FlaskForm):
    usuario = StringField(
        "Usuario",
        validators=[DataRequired(message="El usuario es obligatorio."),
                    Length(min=4, max=50, message="Debe tener entre 4 y 50 caracteres.")]
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria."),
                    Length(min=6, message="Debe tener al menos 6 caracteres.")]
    )
    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(message="Confirme la contraseña."),
                    EqualTo('password', message="Las contraseñas no coinciden.")]
    )
    submit = SubmitField("Registrarse")