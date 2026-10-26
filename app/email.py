import requests
from flask import current_app


def send_simple_message(to, subject, text):
    """Envia um e-mail via API do Mailgun. Retorna True se aceito."""
    app = current_app._get_current_object()
    subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject

    if not (app.config['API_URL'] and app.config['API_KEY'] and app.config['API_FROM']):
        app.logger.error('Mailgun não configurado: defina API_URL, API_KEY e API_FROM no .env')
        return False

    try:
        resposta = requests.post(
            app.config['API_URL'],
            auth=('api', app.config['API_KEY']),
            data={'from': app.config['API_FROM'], 'to': to,
                  'subject': subject, 'text': text},
            timeout=10)
    except requests.RequestException as e:
        app.logger.error('Falha ao enviar e-mail para %s: %s', to, e)
        return False

    if resposta.ok:
        app.logger.info('E-mail enviado para %s (%s)', to, resposta.status_code)
        return True
    app.logger.error('Mailgun recusou o envio para %s: %s %s',
                     to, resposta.status_code, resposta.text)
    return False


def notify_new_user(username, email=None):
    """Notifica cadastro de novo usuário. Retorna True se ao menos um envio funcionou."""
    config = current_app.config
    text = ('Prontuário: {}\nNome: {}\nNovo usuário cadastrado: {}'
            .format(config['FLASKY_PRONTUARIO'], config['FLASKY_NAME'], username))
    recipients = [config['FLASKY_NOTIFY'], config['FLASKY_ADMIN'], email]
    # um POST por destinatário: o sandbox do Mailgun recusa quem não foi autorizado
    # e isso não deve impedir os demais envios
    results = [send_simple_message(r, 'Novo usuário', text)
               for r in dict.fromkeys(r for r in recipients if r)]
    return any(results)
