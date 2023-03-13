from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class UploadVideoForm(FlaskForm):
    version = StringField("Версия")
    file = FileField("Выберите файл")
    description = TextAreaField("Описание версии")
    submit = SubmitField("Готово")