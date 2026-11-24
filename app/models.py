from . import db


class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    alunos = db.relationship('Aluno', backref='disciplina', lazy='dynamic')

    NOMES_INICIAIS = ['DSWA5', 'GPSA5', 'TCOA5']

    @staticmethod
    def insert_disciplinas():
        for nome in Disciplina.NOMES_INICIAIS:
            if Disciplina.query.filter_by(nome=nome).first() is None:
                db.session.add(Disciplina(nome=nome))
        db.session.commit()

    def __repr__(self):
        return '<Disciplina %r>' % self.nome


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'),
                              nullable=False)

    def __repr__(self):
        return '<Aluno %r>' % self.nome
