import os
from flask import Flask
from config import Config

def create_app(test_config: dict=None, config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(config_class)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    from .db import db, init_app
    
    db.init_app(app)
    init_app(app)

    return app