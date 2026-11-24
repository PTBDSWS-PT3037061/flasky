from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class AlunoForm(FlaskForm):
    nome = StringField('Cadastre o novo Aluno:',
                       validators=[DataRequired(), Length(1, 64)])
    disciplina = SelectField('Disciplina associada:', coerce=int)
    submit = SubmitField('Cadastrar')
