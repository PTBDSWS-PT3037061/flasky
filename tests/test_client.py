import unittest
from app import create_app, db
from app.models import User


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email, 'password': password}, follow_redirects=True)

    def test_home_page_anonimo(self):
        response = self.client.get('/')
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Avaliação contínua: <b>Aula 090</b>', html)
        self.assertIn('Olá, Desconhecido!', html)
        self.assertNotIn('Relação de usuários cadastrados', html)

    def test_home_page_lista_usuarios_quando_logado(self):
        db.session.add_all([
            User(email='ana@example.com', username='ana',
                 password='cat', confirmed=True),
            User(email='bia@example.com', username='bia',
                 password='dog', confirmed=False)])
        db.session.commit()
        html = self.login('ana@example.com', 'cat').get_data(as_text=True)
        self.assertIn('Olá, ana!', html)
        self.assertIn('Relação de usuários cadastrados', html)
        self.assertIn('<td>bia@example.com</td>', html)
        self.assertIn('<td>True</td>', html)
        self.assertIn('<td>False</td>', html)

    def test_cadastro_confirmacao_e_logout(self):
        response = self.client.post('/auth/register', data={
            'email': 'caio@example.com', 'username': 'caio',
            'password': 'cat', 'password2': 'cat'}, follow_redirects=True)
        html = response.get_data(as_text=True)
        self.assertIn('A confirmation email has been sent', html)

        html = self.login('caio@example.com', 'cat').get_data(as_text=True)
        self.assertIn('Você ainda não confirmou a sua conta.', html)
        self.assertIn('Flasky - Confirme a sua conta', html)

        user = User.query.filter_by(email='caio@example.com').first()
        token = user.generate_confirmation_token()
        html = self.client.get('/auth/confirm/' + token,
                               follow_redirects=True).get_data(as_text=True)
        self.assertIn('You have confirmed your account', html)
        self.assertIn('Olá, caio!', html)
        self.assertIn('Relação de usuários cadastrados', html)

        html = self.client.get('/auth/logout',
                               follow_redirects=True).get_data(as_text=True)
        self.assertIn('You have been logged out.', html)
        self.assertIn('Olá, Desconhecido!', html)
