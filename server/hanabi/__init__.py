from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config[config_name].init_app(app)

    db.init_app(app)

    from .api.v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app