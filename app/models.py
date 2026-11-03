import time
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from . import db, login_manager


def _make_token(data, expiration):
    """Gera um token assinado que vale por `expiration` segundos."""
    s = Serializer(current_app.config['SECRET_KEY'])
    return s.dumps(dict(data, exp=time.time() + expiration))


def _load_token(token):
    """Lê um token; devolve None se for inválido ou estiver expirado."""
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except Exception:
        return None
    if not isinstance(data, dict) or data.get('exp', 0) < time.time():
        return None
    return data


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        # usuários antigos (criados antes do login) não têm senha
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        return _make_token({'confirm': self.id}, expiration)

    def confirm(self, token):
        data = _load_token(token)
        if data is None or data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        return _make_token({'reset': self.id}, expiration)

    @staticmethod
    def reset_password(token, new_password):
        data = _load_token(token)
        if data is None or data.get('reset') is None:
            return False
        user = db.session.get(User, data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        return _make_token(
            {'change_email': self.id, 'new_email': new_email}, expiration)

    @staticmethod
    def from_email_change_token(token):
        """Devolve o usuário dono de um token de troca de e-mail válido."""
        data = _load_token(token)
        if data is None or data.get('change_email') is None:
            return None
        return db.session.get(User, data.get('change_email'))

    def change_email(self, token):
        data = _load_token(token)
        if data is None or data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
