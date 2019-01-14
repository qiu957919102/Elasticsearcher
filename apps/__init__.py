# -*- coding: utf-8 -*-

from flask import Flask
from apps.api import api


def register_blueprint(app, target):
    app.register_blueprint(target)


def create_app():
    app = Flask(__name__)

    app.config.from_object('apps.settings')
    app.config.from_object('apps.security')

    register_blueprint(app, api)

    return app
