#!/usr/bin/env python3

# Core lib
import json
import requests
import traceback
from os import environ

from flask import Flask             # Classe do Flask
from flask import request           # Objeto de requisições recebidas
from flask_restful import Api       # Classe da extensão
from flask_restful import Resource  # Classe de abstração de recurso REST

def deal_with_event(data):
    '''Handler para as requests recebidas

    Args:
        data (string): Payload em formato json.
            Contêm informações do card a ser criado.

    Returns:
        tuple: Mensagem de status de execução, código HTTP
    '''

    def open_issue(data):
        '''
        --- TODO: DOCS --
        '''

        for alert in data['alerts']:
            payload = {
                "x-auth-token":environ['X_AUTH_TOKEN'],
                "level":"0",
                "message":alert['labels']['alertname'] + " - Details: " + alert['annotations']['description'] + " - URL: " + alert['generatorURL'],
                "metId":"",
                "severity":alert['labels']['severity'],
                "source":"lambda",
                "subsystemId":"",
                "suppressionKey":"",
                "ciType":"1",
                "ciName":"",
                "custom1":json.dumps(alert),
                "custom2":"",
                "custom3":"",
                "custom4":"",
                "custom5":"",
                "status":alert['status'],
                "entity":""
            }
            requests.post(environ['WEBHOOK_URL'], json=payload)

        return 'Issue created.', 201

    # -------------------------------------------------
    try:
        return open_issue(data)

    except Exception as error:
        notify('ERROR: Alert-Sender', traceback.format_exc())
        return 'Something went wrong opening the issue.', 500


def notify(subject, data):
    from smtplib import SMTP
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    from_addr = environ['ERROR_MAIL_LOGIN']
    to_addr = environ['ERROR_MAIL_LOGIN']

    try:
        msg = MIMEMultipart()
        msg['To'] = to_addr
        msg['From'] = from_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(str(data), 'plain'))

        svr = SMTP('smtp.gmail.com', 587)
        svr.ehlo()
        svr.starttls()
        svr.ehlo()
        svr.login(
            environ['ERROR_MAIL_LOGIN'],
            environ['ERROR_MAIL_PASS']
        )

        svr.sendmail(from_addr, to_addr, msg.as_string())

    except Exception as err:
        return str(err.args[0]), 200

    return 'Email sent.', 200

class LambdaStatusChecker(Resource):
    '''Handler do recurso '/status'.

    Este recurso tem como único objetivo indicar que o endpoint está funcional
    e pode ser consumido. Ex:

    Example:
        GET https://abc123.execute-api.us-east-1.amazonaws.com/dev/status

        HTTP/1.1 200 OK
        "I'm alive!"
    '''

    def get(self):
        '''Handler do método GET.

        Returns:
            string: Mensagem 'eu estou vivo!', caso esteja.
        '''
        return "I'm alive!"


class LambdaHookHandler(Resource):
    '''
    Handler do recurso '/hook'.
    '''

    def post(self):
        '''Handler do método POST.

        Tenta iterar o objeto 'messages' do payload recebido e verificar o tipo
        de evento de cada mensagem. Caso o método consiga iterar o objeto, o
        evento será direcionado para a função 'deal_with_event'. Caso
        contrário, o método imprimirá a mensagem de erro e finalizará com
        código 400 (bad request).

        Returns:
            tuple: Mensagem de status de execução, código HTTP
        '''
        data = request.get_json()

        return deal_with_event(data)


# Objeto do Flask utilizado como entrypoint do Lambda, deve permanecer global
app = Flask(__name__)

# Objeto do Flask-Restful, define as rotas e as classes de handling
rest = Api(app)
rest.add_resource(LambdaHookHandler, '/hook')
rest.add_resource(LambdaStatusChecker, '/status')


if __name__ == '__main__':
    # Entrypoint no caso de execução local.
    app.run(debug=True, host='0.0.0.0', port=5001)
