from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from passlib.hash import bcrypt
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONFIG
import os  # Import os module
import logging

# Carregar o arquivo .env
load_dotenv()

# Obter string de conexão da variável de ambiente
connection_string = os.getenv('DATABASE_URL')

# Inicializa o SQLAlchemy globalmente
db = SQLAlchemy()

# Define o modelo Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.usuario}>'

    def json(self):
        return {'id': self.id, 'usuario': self.usuario, 'nome': self.nome, 'email': self.email, 'senha': self.senha}

def create_app():
    app = Flask(__name__)

    # Configura a URI do banco de dados para o SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'super-secret') # Configure a chave secreta JWT
    jwt = JWTManager(app)

    # Inicializa o SQLAlchemy com a aplicação Flask
    db.init_app(app)

    # Cria as tabelas do banco de dados
    with app.app_context():
        db.create_all()
#Login
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('index.html')
        elif request.method == 'POST':
            usuario = request.json.get('usuario')
            senha = request.json.get('senha')
            if not usuario or not senha:
                return jsonify({'msg': 'usuario e senha são obrigatórios'}), 400

            # Buscar o usuário no banco de dados pelo username
            user = Usuario.query.filter_by(usuario=usuario).first()

            if not user:
                return jsonify({'msg': 'Usuário não existe'}), 401

            # Verificar se a senha fornecida corresponde ao hash armazenado no banco de dados
            if bcrypt.verify(senha, user.senha):
                access_token = create_access_token(identity=usuario)
                return jsonify(access_token=access_token), 200
                #return render_template('sucesso.html')
            else:
                #return render_template('falha.html')
                return jsonify({'msg': 'Senha incorreta'}), 401

     # Criar usuário
    @app.route('/usuario', methods=['POST'])
    def create_user():
        try:
            data = request.get_json()
            usuario = data['usuario']
            if Usuario.query.filter_by(usuario=usuario).first():
                return jsonify({'message': 'Este usuario já existe!'}), 409
            nome = data['nome']
            email = data['email']
            senha = data['senha']

            # Hashear a senha            
            hashed_password_str = bcrypt.hash(senha)
            
            new_user = Usuario(usuario=usuario, nome=nome, email=email, senha=hashed_password_str)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'Usuário criado'}), 201
        except KeyError as e:
            db.session.rollback()
            logging.error(f"Erro ao criar usuário (dados ausentes): {e}")
            return jsonify({'message': f'missing data: {e}'}), 400
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao criar usuário: {e}")
            return jsonify({'message': 'Erro ao criar usuário'}), 500
           
# ESTE TRECHO NÃO ESTÁ FUNCIONANDO AINDA
    @app.route('/protegido', methods=['GET'])
    @jwt_required()
    def protegido():
        current_user = get_jwt_identity()
        #return render_template('sucesso.html')
        return jsonify(logado_como=current_user), 200

    # Lista todos os usuários
    @app.route('/usuario', methods=['GET'])
    def get_users():
        try:
            users = Usuario.query.all()
            return jsonify([usuario.json() for usuario in users]), 200
        except Exception as e:
            logging.error(f"Erro ao obter usuários: {e}")
            return jsonify({'message': 'Erro ao obter usuários'}), 500
        
 # Lista usuário por ID
    @app.route('/usuario/<id>', methods=['GET'])
    def get_user_by_id(id):
        try:
            users = Usuario.query.get(id)
            if users:
               return jsonify(users.json()), 200
            else:
                return jsonify({'message': 'usuario não encontrado'}), 404
        except Exception as e:
            logging.error(f"Erro ao obter usuários com ID {id}: {e}")
            return jsonify({'message': 'erro ao obter usuario'}), 500

    # Atualizar
    @app.route("/usuario/<int:id>", methods=["PUT"])
    def update_usuario(id):
        usuario_objeto = Usuario.query.filter_by(id=id).first()
        if usuario_objeto:
            body = request.get_json()
            if body:
                try:
                    if 'usuario' in body:
                        usuario_objeto.usuario = body['usuario']
                    if 'nome' in body:
                        usuario_objeto.nome = body['nome']
                    if 'email' in body:
                        usuario_objeto.email = body['email']
                    if 'senha' in body:
                        usuario_objeto.senha = body['senha']
                        usuario_objeto.senha = bcrypt.hash(body['senha'])

                    db.session.commit()
                    return jsonify({'message': 'Usuário atualizado com sucesso', 'usuario': usuario_objeto.json()}), 200
                except Exception as e:
                    print('Erro', e)
                    db.session.rollback()
                    return jsonify({'message': 'Erro ao atualizar usuário'}), 400
            else:
                return jsonify({'message': 'Campo vazio'}), 400
        return jsonify({'message': 'Usuário não encontrado'}), 404

    # Deletar
    @app.route("/usuario/<int:id>", methods=["DELETE"])
    def deleta_usuario(id):
        usuario_objeto = Usuario.query.filter_by(id=id).first()
        if usuario_objeto:
            try:
                db.session.delete(usuario_objeto)
                db.session.commit()
                return jsonify({'message': 'usuario removido com sucesso'}), 200
            except Exception as e:
                print('Erro', e)
                db.session.rollback()  # Em caso de erro, desfaz as alterações na sessão
                return jsonify({'message': 'erro ao remover usário'}), 400
        return jsonify({'message': 'usuário não encontrado'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)