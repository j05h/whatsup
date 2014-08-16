from flask import Flask
from flask_environments import Environments


app = Flask(__name__)
env = Environments(app)
env.from_object('whatsup.config')

# TODO(retr0h): No idea why these are imported here.
from whatsup.app import views
from whatsup.app import api
