from datetime import datetime, timezone
from flask import render_template, redirect, url_for, current_app, flash
from . import main
from .forms import AlunoForm
from .. import db
from ..models import Aluno, Disciplina


@main.route('/')
def index():
    return render_template('index.html',
                           nome=current_app.config['FLASKY_NAME'],
                           prontuario=current_app.config['FLASKY_PRONTUARIO'],
                           current_time=datetime.now(timezone.utc))


@main.route('/alunos', methods=['GET', 'POST'])
def alunos():
    form = AlunoForm()
    form.disciplina.choices = [(d.id, d.nome) for d in Disciplina.ordenadas()]
    if form.validate_on_submit():
        db.session.add(Aluno(nome=form.nome.data.strip(),
                             disciplina_id=form.disciplina.data))
        db.session.commit()
        flash('Estudante cadastrado com sucesso!')
        return redirect(url_for('.alunos'))
    lista = Aluno.query.order_by(Aluno.id).all()
    return render_template('alunos.html', form=form, alunos=lista)


# Módulos não desenvolvidos: apenas exibem a página "Não disponível"
@main.route('/professores')
@main.route('/disciplinas')
@main.route('/cursos')
@main.route('/ocorrencias')
def nao_disponivel():
    return render_template('nao_disponivel.html',
                           current_time=datetime.now(timezone.utc))
