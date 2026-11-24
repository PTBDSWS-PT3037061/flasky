import unittest
from app import create_app, db
from app.models import Aluno, Disciplina


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn('Prontuário:', html)
        self.assertIn('A data e hora local', html)

    def test_disciplinas_iniciais(self):
        nomes = [d.nome for d in Disciplina.ordenadas()]
        self.assertEqual(nomes, ['DSWA5', 'GPSA5', 'IHCA5',
                                 'SODA5', 'PJIA5', 'TCOA5'])

    def test_cadastro_aluno(self):
        tcoa5 = Disciplina.query.filter_by(nome='TCOA5').first()
        r = self.client.post('/alunos',
                             data={'nome': 'Fulano', 'disciplina': tcoa5.id},
                             follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Aluno.query.count(), 1)
        html = r.get_data(as_text=True)
        self.assertIn('Fulano', html)
        self.assertIn('TCOA5', html)
        self.assertIn('Estudante cadastrado com sucesso!', html)

    def test_cadastro_sem_nome(self):
        r = self.client.post('/alunos', data={'nome': '', 'disciplina': 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Aluno.query.count(), 0)

    def test_nao_disponivel(self):
        for rota in ['/professores', '/disciplinas', '/cursos', '/ocorrencias']:
            r = self.client.get(rota)
            self.assertEqual(r.status_code, 200)
            self.assertIn('Não disponível', r.get_data(as_text=True))

    def test_404(self):
        self.assertEqual(self.client.get('/inexistente').status_code, 404)
