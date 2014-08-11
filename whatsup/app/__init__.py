from flask import Flask
from flask_environments import Environments

app = Flask(__name__)
env = Environments(app)
env.from_object('config')

from whatsup.app import views
from whatsup.app import api
