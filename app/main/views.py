from flask import render_template, session, redirect, url_for
from .. import db
from ..models import User, Role
from ..email import notify_new_user
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            role = Role.query.filter_by(name='User').first()
            if role is None:
                role = Role(name='User')
            user = User(username=form.name.data,
                        email=form.email.data or None, role=role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            session['email_sent'] = notify_new_user(user.username, user.email)
        else:
            session['known'] = True
            session['email_sent'] = False
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           email_sent=session.get('email_sent', False),
                           users=User.query.all())
