import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from extensions import db, jwt
from flask import Flask
from dotenv import load_dotenv
from blueprints.usuario.usuario import usuario_bp
from blueprints.despesa.despesa import despesa_bp
from blueprints.categoria.categoria import categoria_bp
from flask_cors import CORS  # Import Flask-CORS

load_dotenv()

def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        # Banco em memória para testes
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret'
    else:
        # Banco real para produção/desenvolvimento
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"postgresql://{os.environ.get('DATABASE_USER')}:"
            f"{os.environ.get('DATABASE_PASSWORD')}@"
            f"{os.environ.get('DATABASE_HOST')}:"
            f"{os.environ.get('DATABASE_PORT')}/"
            f"{os.environ.get('DATABASE_DATABASE')}"
        )
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret') 

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    app.register_blueprint(despesa_bp, url_prefix='/despesa')
    app.register_blueprint(usuario_bp)
    app.register_blueprint(categoria_bp, url_prefix='/categoria')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
