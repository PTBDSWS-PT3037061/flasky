import os

from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# ============================================================
# CONFIGURAÇÃO
# ============================================================

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


bootstrap = Bootstrap(app)
moment = Moment(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ============================================================
# MODELOS
# ============================================================

class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(64),
        unique=True,
        nullable=False
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
        index=True,
        nullable=False
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id')
    )

    def __repr__(self):
        return '<User %r>' % self.username


# ============================================================
# FORMULÁRIO
# ============================================================

class NameForm(FlaskForm):

    name = StringField(
        'What is your name?',
        validators=[DataRequired()]
    )

    role = SelectField(
        'Role?:',
        choices=[
            ('Administrator', 'Administrator'),
            ('Moderator', 'Moderator'),
            ('User', 'User')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField('Submit')


# ============================================================
# GARANTIR QUE AS 3 FUNÇÕES EXISTAM
# ============================================================

def create_default_roles():

    role_names = [
        'Administrator',
        'Moderator',
        'User'
    ]

    roles = {}

    for role_name in role_names:

        role = Role.query.filter_by(
            name=role_name
        ).first()

        # só cria caso ainda não exista
        if role is None:

            role = Role(
                name=role_name
            )

            db.session.add(role)

        roles[role_name] = role

    db.session.commit()

    return roles


# ============================================================
# SHELL
# ============================================================

@app.shell_context_processor
def make_shell_context():

    return dict(
        db=db,
        User=User,
        Role=Role
    )


# ============================================================
# ERROS
# ============================================================

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


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    # garante que Administrator, Moderator e User existam
    roles_dictionary = create_default_roles()

    if form.validate_on_submit():

        username = form.name.data.strip()

        # procura usuário existente
        user = User.query.filter_by(
            username=username
        ).first()

        if user is None:

            # pega a função escolhida no select
            selected_role = roles_dictionary[
                form.role.data
            ]

            # cria o usuário com a função selecionada
            user = User(
                username=username,
                role=selected_role
            )

            db.session.add(user)

            # persistência no banco
            db.session.commit()

            session['known'] = False

        else:

            session['known'] = True

        session['name'] = username

        return redirect(
            url_for('index')
        )

    # ========================================================
    # LISTAGEM DE USUÁRIOS
    # ========================================================

    users = User.query.order_by(
        User.id
    ).all()

    # ========================================================
    # LISTAGEM DE FUNÇÕES
    # ========================================================

    roles = Role.query.order_by(
        Role.id
    ).all()

    # ========================================================
    # CONTADORES
    # ========================================================

    users_count = User.query.count()

    roles_count = Role.query.count()

    # ========================================================
    # USUÁRIOS AGRUPADOS POR FUNÇÃO
    # ========================================================

    grouped_roles = []

    for role in roles:

        role_users = role.users.order_by(
            User.id
        ).all()

        grouped_roles.append({
            'role': role,
            'users': role_users
        })

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        known=session.get('known', False),
        users=users,
        roles=roles,
        users_count=users_count,
        roles_count=roles_count,
        grouped_roles=grouped_roles
    )


if __name__ == '__main__':
    app.run(debug=True)