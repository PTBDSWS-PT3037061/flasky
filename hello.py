import os
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'hard to guess string'
)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

FLASKY_ADMIN = os.getenv('FLASKY_ADMIN')
API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')
API_FROM = os.getenv('API_FROM')
FLASKY_NAME = os.getenv('FLASKY_NAME')
FLASKY_PRONTUARIO = os.getenv('FLASKY_PRONTUARIO')

PROFESSOR_EMAIL = 'flaskaulasweb@zohomail.com'


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(64),
        unique=True
    )

    users = db.relationship(
        'User',
        backref='role',
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(64),
        unique=True,
        index=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id')
    )

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):

    name = StringField(
        'Qual é o seu nome?',
        validators=[DataRequired()]
    )

    send_professor = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField('Submit')


def get_user_role():

    role = Role.query.filter_by(
        name='User'
    ).first()

    if role is None:

        role = Role(
            name='User'
        )

        db.session.add(role)
        db.session.commit()

    return role


def send_registration_email(recipient, user):

    if not API_URL:
        raise RuntimeError('API_URL não configurada.')

    if not API_KEY:
        raise RuntimeError('API_KEY não configurada.')

    if not API_FROM:
        raise RuntimeError('API_FROM não configurado.')

    body = f"""
Novo usuário cadastrado na aplicação Flask.

Prontuário: {FLASKY_PRONTUARIO}
Nome do aluno: {FLASKY_NAME}
Usuário cadastrado: {user.username}
"""

    response = requests.post(
        API_URL,
        auth=(
            'api',
            API_KEY
        ),
        data={
            'from': API_FROM,
            'to': recipient,
            'subject': 'Novo usuário cadastrado',
            'text': body
        },
        timeout=15
    )

    response.raise_for_status()

    return response.json()


@app.shell_context_processor
def make_shell_context():

    return dict(
        db=db,
        User=User,
        Role=Role
    )


@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        '404.html'
    ), 404


@app.errorhandler(500)
def internal_server_error(e):

    return render_template(
        '500.html'
    ), 500


@app.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        username = form.name.data.strip()

        user = User.query.filter_by(
            username=username
        ).first()

        session['email_sent'] = False

        if user is None:

            user_role = get_user_role()

            user = User(
                username=username,
                role=user_role
            )

            db.session.add(user)
            db.session.commit()

            session['known'] = False

            try:

                send_registration_email(
                    FLASKY_ADMIN,
                    user
                )

                session['email_sent'] = True

            except Exception as error:

                print(
                    'Erro ao enviar e-mail institucional:',
                    error
                )

            if form.send_professor.data:

                try:

                    send_registration_email(
                        PROFESSOR_EMAIL,
                        user
                    )

                except Exception as error:

                    print(
                        'Erro ao enviar e-mail para o professor:',
                        error
                    )

        else:

            session['known'] = True

        session['name'] = username

        return redirect(
            url_for('index')
        )

    users = User.query.order_by(
        User.id
    ).all()

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        known=session.get('known', False),
        email_sent=session.get('email_sent', False),
        users=users
    )


if __name__ == '__main__':
    app.run(debug=True)