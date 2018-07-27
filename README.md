# alert-sender

`alert-sender` é uma função lambda com o objetivo de tratar e redirecionar uma request HTML.


## Funcionamento

A lambda expõe duas rotas: `/status` e `/hook`. A primeira deve ser consumida
via GET e sua única função é informar se a lambda está preparada para receber
webhooks do PagerDuty. A segunda rota deve ser consumida via POST e é de fato
quem recebe as requisições (webhooks) e as trata de acordo com o tipo do evento.

Esta é uma lambda basica para tratar e redirecionar qualquer tipo de payload.


## Requerimentos

A função requer o Python3, na versão 3.6. As seguintes bibliotecas de terceiro
fora utilizadas:

- [zappa](https://www.zappa.io)
- [flask](http://flask.pocoo.org)
- [flask-restful](https://flask-restful.readthedocs.io)

PS: O `zappa` já inclui `flask`.


## Deployment

O deployment é realizado através do `zappa`.


- Crie um virtualenv para a função lambda

```sh
$ virtualenv alert-lambda
```

- Instale as dependências

```sh
$ ./alert-lambda/bin/pip3 install zappa flask-restful
```

- Clone este repo

```sh
$ git clone git@gitlab.com:Rivendel-Monit/lambdas/alert-sender.git
```

- Mova a função lambda e a configuração do Zappa para o virtualenv

```sh
$ mv alert-sender/alert-sender.py alert-lambda/ && mv alert-sender/zappa_settings.json alert-lambda/
```

- Altere os valores das variáveis de ambiente na configuração do `zappa`

```sh
$ vim alert-lambda/zappa_settings.json
```

- Ative a virtualenv

```sh
$ cd alert-lambda && source ./bin/activate
```

- Faça o deploy

```sh
$ zappa deploy dev
```


### Variáveis de ambiente

A lambda requer as seguintes variáveis de ambiente:

- `ERROR_MAIL_LOGIN`: Nome de usuário do email que recebera caso de erro.
- `ERROR_MAIL_PASS`: Senha do usuário do email que recebera caso de erro.
- `WEBHOOK_URL`: URL do servidor que a payload deve ser direcionada.
- `X_AUTH_TOKEN`: Token de autenticação da payload.
