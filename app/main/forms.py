from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    email = StringField('Qual é o seu email (Envio de notificação do novo usuário)?',
                        validators=[Optional(), Email()])
    submit = SubmitField('Submit')


class EditUserForm(FlaskForm):
    name = StringField('Nome do usuário', validators=[DataRequired()])
    submit = SubmitField('Salvar')


class DeleteForm(FlaskForm):
    submit = SubmitField('Excluir')
