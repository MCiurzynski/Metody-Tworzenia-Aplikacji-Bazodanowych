import os
from flask import Flask
from config import Config
from app.db import db, init_app, User
from flask_login import LoginManager

login_manager = LoginManager()

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
    
    
    init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Zaloguj się, aby uzyskać dostęp."

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)
    
    from app.routes.gym import gym_bp

    app.register_blueprint(gym_bp)

    from app.routes.clients import clients_bp

    app.register_blueprint(clients_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))