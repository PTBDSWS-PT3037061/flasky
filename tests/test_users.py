import unittest
from app import create_app, db
from app.models import User


class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username='joao', email='joao@test')
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_lists_actions(self):
        html = self.client.get('/').get_data(as_text=True)
        self.assertIn('Editar', html)
        self.assertIn('Excluir', html)
        self.assertIn('Deseja realmente excluir este usuário?', html)

    def test_edit_user(self):
        r = self.client.post('/user/%d/edit' % self.user.id,
                             data={'name': 'maria'})
        self.assertEqual(r.status_code, 302)
        user = db.session.get(User, self.user.id)
        self.assertEqual(user.username, 'maria')
        self.assertEqual(user.email, 'joao@test')

    def test_edit_rejects_duplicate_name(self):
        db.session.add(User(username='ana'))
        db.session.commit()
        self.client.post('/user/%d/edit' % self.user.id, data={'name': 'ana'})
        self.assertEqual(db.session.get(User, self.user.id).username, 'joao')

    def test_delete_user(self):
        r = self.client.post('/user/%d/delete' % self.user.id)
        self.assertEqual(r.status_code, 302)
        self.assertIsNone(db.session.get(User, self.user.id))
        html = self.client.get('/').get_data(as_text=True)
        self.assertIn('Usuário removido com sucesso.', html)

    def test_missing_user_404(self):
        self.assertEqual(self.client.post('/user/999/edit', data={'name': 'x'}).status_code, 404)
        self.assertEqual(self.client.post('/user/999/delete').status_code, 404)
