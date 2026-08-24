from flask import Flask, render_template, session, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_aqui'
bootstrap = Bootstrap(app)
moment = Moment(app)

class HomeForm(FlaskForm):
    nome = StringField('Informe o seu nome', validators=[DataRequired()])
    sobrenome = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua Insituição de ensino:', validators=[DataRequired()])
    disciplina = SelectField('Informe a sua disciplina:', choices=[('DSWA5', 'DSWA5')])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    if form.validate_on_submit():
        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        session['ip'] = request.remote_addr
        session['host'] = request.host
        return redirect(url_for('index'))
    return render_template('index.html', form=form, 
                           nome=session.get('nome'), 
                           sobrenome=session.get('sobrenome'), 
                           instituicao=session.get('instituicao'), 
                           disciplina=session.get('disciplina'), 
                           ip=session.get('ip'), 
                           host=session.get('host'), 
                           current_time=datetime.utcnow())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', form=form, current_time=datetime.utcnow())