import os
from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv
from app import database
from .extensions import bcrypt, jwt, limiter

def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    from .routes.auth import auth_bp
    from .routes.transacoes import transacoes_bp
    from .routes.contas import contas_bp
    from .routes.categorias import categorias_bp
    from .routes.relatorios import relatorios_bp
    from .routes.transferencias import transferencias_bp
    from .routes.metas import metas_bp
    from .routes.usuarios import usuarios_bp
    from .routes.dashboard import dashboard_bp
    from .routes.alertas import alertas_bp

    with app.app_context():
        database.iniciar_pool()

    app.register_blueprint(auth_bp)
    app.register_blueprint(transacoes_bp)
    app.register_blueprint(contas_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(transferencias_bp)
    app.register_blueprint(metas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alertas_bp)

    return app