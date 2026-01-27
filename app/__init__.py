from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.paradas import paradas_bp
    from app.routes.rutas import rutas_bp
    from app.routes.grafo import grafo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(paradas_bp)
    app.register_blueprint(rutas_bp)
    app.register_blueprint(grafo_bp)

    return app
