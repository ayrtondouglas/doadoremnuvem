import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import flask_monitoringdashboard as dashboard
import logging
from dynaconf import FlaskDynaconf
from .config import settings as conf
from .mongoDBConf import MongoDBConf
from .core.persistencia.mongodbRepositorio import *

"""
    ----------------------------------------------------
    Doador em Nuvem
    Projeto desenvolvido na disciplina de mestrado do IFPB
    Engenharia de Software
    ----------------------------------------------------
"""

__autor__ = "Ayrton Douglas, Daniel Brandão, Danilo Marcolino Tavares, Poliana Campelo, Thiago Gonçalo"
__propriedade__ = "IFPB e alunos"
__creditos__ = "Alunos da disciplina de Engenharia de Software 2021.1"
__versao__ = conf.versao
__sistema__ = 'Doador em Nuvem ({})'.format(__versao__)
__data_criacao__ = "10/04/21"

""" INIT CONF """
# Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
dashboard.bind(app)
# dynaconf
os.environ['DYNACONF_PORT'] = '9900'
FlaskDynaconf(app, settings_files=["settings.toml"])
print("ENV -> DYNACONF_PORT:", os.environ['DYNACONF_PORT'])
# Conf MongoDB

print('auto_start_docker_mongodb:', conf.auto_start_docker_mongodb)
print('verificando conexão com mongodb...')
mongoDBonline = mongodbOnline(MongoDBConf())
# exige status atualizado do banco de dados
print('mongodb-online: ', mongoDBonline)
# auto start docker - exclusivo para docker
if conf.auto_start_docker_mongodb and mongoDBonline == False:
    print('inicializando mongodb via docker...')
    print('container_is_mongodb:', conf.container_is_mongodb)
    os.system('docker start {}'.format(conf.container_is_mongodb))
    mongoDBonline = mongodbOnline(MongoDBConf())
    print('mongodb-online: ', mongoDBonline)

print('sistema/versão:', __sistema__)

""" SERVIÇOS """


# Historico
@app.route('/api/historico/salvar', methods=['GET', 'POST'])
def salvarHistorico():
    msg = ''
    print('salvarHistorico...')
    try:
        if mongoDBonline:
            # executa metodo principal
            print('request-status:', request.args.get("status"))
            print('request-tp_operacao:', request.args.get("tp_operacao"))
            print('request-ds_log:', request.args.get("ds_log"))
            print('request-qt_doadores_notificados:', request.args.get("qt_doadores_notificados"))
            if testeParametrosHistorico(request):
                msg = 'Parametros nulos'
            else:
                # salvar
                salvarHistoricoBD(request.args.get("status"),
                                  request.args.get("tp_operacao"),
                                  request.args.get("ds_log"),
                                  request.args.get("qt_doadores_notificados"),
                                  MongoDBConf())
                msg = 'Sucesso ao salvar histórico!'
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicacao com mongodb!')
    except Exception as e:
        logging.error(e)
        msg = 'Falha geral'
        raise Exception("Ocorreu um erro geral!")
    return jsonify(msg)

# Usuario
@app.route('/api/usuarios/salvar', methods=['GET', 'POST'])
def salvarUsuario():
    msg = ''
    try:
        if mongoDBonline:
            # executa metodo principal
            print('request-nome:', request.args.get("nome"))
            print('request-perfil:', request.args.get("perfil"))
            print('request-cpf:', request.args.get("cpf"))
            print('request-email:', request.args.get("email"))
            print('request-endereco:', request.args.get("endereco"))
            print('request-telefone:', request.args.get("telefone"))
            print('request-senha:', request.args.get("senha"))
            if testeParametrosUsuario(request):
                msg = 'Parametros nulos'
                return msg, 400
            elif buscarUsuarioPorCpfBD(int(request.args.get("cpf")), MongoDBConf()):
                msg = 'Já existe usuário com o mesmo CPF cadastrado.'
                return msg, 400
            else:
                # salvar
                salvarUsuarioBD(request.args.get("nome"),
                                request.args.get("perfil"),
                                int(request.args.get("cpf")),
                                request.args.get("email"),
                                request.args.get("endereco"),
                                request.args.get("telefone"),
                                request.args.get("senha"),
                                MongoDBConf())
                msg = 'Sucesso ao salvar usuário!'
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicacao com mongodb!')
    except Exception as e:
        logging.error(e)
        msg = 'Falha geral'
        raise Exception("Ocorreu um erro geral!")
    return jsonify(msg)

@app.route('/api/usuarios/editar', methods=['GET', 'POST'])
def editarUsuario():
    msg = ''
    try:
        if mongoDBonline:
            # executa metodo principal
            print('request-nome:', request.args.get("nome"))
            print('request-perfil:', request.args.get("perfil"))
            print('request-cpf:', request.args.get("cpf"))
            print('request-email:', request.args.get("email"))
            print('request-endereco:', request.args.get("endereco"))
            print('request-telefone:', request.args.get("telefone"))
            print('request-senha:', request.args.get("senha"))
            # validacao
            if testeParametrosUsuario(request):
                msg = 'Parametros nulos'
                return msg, 400
            else:
                # salvar
                editarUsuarioBD(request.args.get("nome"),
                                request.args.get("perfil"),
                                int(request.args.get("cpf")),
                                request.args.get("email"),
                                request.args.get("endereco"),
                                request.args.get("telefone"),
                                request.args.get("senha"),
                                MongoDBConf())
                msg = 'Sucesso ao editar usuário!'
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicacao com mongodb!')
    except Exception as e:
        logging.error(e)
        raise Exception("Ocorreu um erro geral!")
    return jsonify(msg)

@app.route('/api/usuarios/excluir', methods=['GET', 'POST'])
def excluirUsuario():
    msg = ''
    try:
        if mongoDBonline:
            if request.args.get("cpf") is None:
                msg = 'Parametros nulos'
                return msg, 400
            else:
                # excluir
                excluirUsuarioBD(int(request.args.get("cpf")), MongoDBConf())
                msg = 'Sucesso ao excluir usuário!'
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicacao com mongodb!')
    except Exception as e:
        logging.error(e)
        raise Exception("Ocorreu um erro geral!")
    return jsonify(msg)

def testeParametrosHistorico(request):
    return (request.args.get("status") is None or request.args.get("tp_operacao") is None
            or request.args.get("ds_log") is None or request.args.get("qt_doadores_notificados") is None)

def testeParametrosUsuario(request):
    return (request.args.get("nome") is None or request.args.get("perfil") is None or
            request.args.get("cpf") is None or request.args.get("email") is None or
            request.args.get("endereco") is None or request.args.get("telefone") is None or
            request.args.get("senha") is None)

# Historico Listar
@app.route('/api/historico/')
@app.route('/api/historico/listar', methods=['GET'])
def listarHistorico():
    try:
        if (mongoDBonline):
            # executa metodo principal
            lista = listarHistoricoBD(MongoDBConf())
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicação com mongodb!')
    except Exception as e:
        logging.error(e)
        raise Exception("Ocorreu um erro geral!")
    return respostaHistoricoJson(lista)

# Usuario Listar
@app.route('/api/usuarios/')
@app.route('/api/usuarios/listar', methods=['GET'])
def listarUsuarios():
    try:
        if (mongoDBonline):
            # executa metodo principal
            lista = listarUsuariosBD(MongoDBConf())
        else:
            print('mongodb: offline')
            raise Exception('Falha de comunicação com mongodb!')
    except Exception as e:
        logging.error(e)
        raise Exception("Ocorreu um erro geral!")
    return respostaUsuarioJson(lista)

# TODO melhorar
def respostaHistoricoJson(lista):
    resposta = list()
    for r in lista:
        resposta.append({'status': r['status'],
                         'dt_operacao': r['dt_operacao'],
                         'tp_operacao': r['tp_operacao'],
                         'ds_log': r['ds_log'],
                         'qt_doadores_notificados': r['qt_doadores_notificados']
                         })
    return jsonify(resposta)

# TODO melhorar
def respostaUsuarioJson(lista):
    resposta = list()
    for r in lista:
        resposta.append({'nome': r['nome'],
                         'perfil': r['perfil'],
                         'cpf': r['cpf'],
                         'email': r['email'],
                         'endereco': r['endereco'],
                         'telefone': r['telefone'],
                         'senha': r['senha']
                         })
    return jsonify(resposta)

# Status
@app.route('/', methods=['GET'])
def statusFlask():
    # verifica novamente mongodb
    mongoDBonline = mongodbOnline(MongoDBConf())

    if request.headers.get('Authorization') == '42':
        return jsonify({"42": "ERRO! Algo de errado ocorreu."})

    return jsonify({"__metodo-ia": __sistema__,
                    "api-rest": 'online',
                    "mongodb": 'online' if mongoDBonline else 'offline'})


# Dynaconf
@app.route("/dynaconf")
def index():
    return render_template("dynaconf.html")


# Main
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
