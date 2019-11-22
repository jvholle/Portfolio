from flask import Flask, config
# SECRET_KEY = 'development'

app = Flask(__name__, instance_relative_config=True)
app.config['TESTING'] = True
#app.config.from_object('config')
app.config.from_pyfile('config.py')
app.secret_key = app.config.get('SECRET_KEY')

from MessBrd_Postgres_V2 import views