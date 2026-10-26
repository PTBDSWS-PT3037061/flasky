import unittest
from unittest import mock
from app import create_app, db
from app.email import notify_new_user


class EmailTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config.update(API_URL='http://mailgun.test', API_KEY='k',
                               API_FROM='from@test', FLASKY_ADMIN='inst@test',
                               FLASKY_NAME='Fulano', FLASKY_PRONTUARIO='PT1')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch('app.email.requests.post')
    def test_notify_sends_to_all_recipients(self, post):
        post.return_value.ok = True
        self.assertTrue(notify_new_user('joao', 'joao@test'))
        tos = [c.kwargs['data']['to'] for c in post.call_args_list]
        self.assertEqual(tos, ['flaskaulasweb@zohomail.com', 'inst@test', 'joao@test'])
        text = post.call_args.kwargs['data']['text']
        self.assertIn('PT1', text)
        self.assertIn('Fulano', text)
        self.assertIn('joao', text)

    @mock.patch('app.email.requests.post')
    def test_failure_returns_false(self, post):
        post.return_value.ok = False
        post.return_value.status_code = 403
        post.return_value.text = 'forbidden'
        self.assertFalse(notify_new_user('joao'))
