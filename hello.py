from flask import Flask, render_template, request, make_response, redirect, abort
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/user/<nome>/<prontuario>/<instituicao>')
def user(nome, prontuario, instituicao):
    return render_template('user.html', nome=nome, prontuario=prontuario, instituicao=instituicao)

@app.route('/contextorequisicao')
def contextorequisicao():
    navegador = request.headers.get('User-Agent')
    ip = request.remote_addr
    host = request.host
    return render_template('contexto.html', nome="Renan Gomes Mota", navegador=navegador, ip=ip, host=host)

@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    return 'Bad request', 400

@app.route('/objetoresposta')
def objetoresposta():
    response = make_response('<h1>Este documento carrega um cookie!</h1>')
    response.set_cookie('meu_cookie', 'valor_teste')
    return response

@app.route('/redirecionamento')
def redirecionamento():
    return redirect('https://www.ifsp.edu.br/')

@app.route('/abortar')
def abortar():
    abort(404)