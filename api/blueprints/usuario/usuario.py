from flask import Flask, Blueprint, jsonify, render_template, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from passlib.hash import bcrypt
from extensions import db
from models import Usuario, Despesa, Categoria
from flask_cors import cross_origin
import logging

usuario_bp = Blueprint('usuario', __name__)

# Configurar logging para depuração
logging.basicConfig(level=logging.INFO)

# Login

@usuario_bp.route('/', methods=['GET', 'POST'])
@cross_origin()
def login():
    if request.method == 'GET':
        # Renderiza o formulário de login
        return render_template('index.html')
    elif request.method == 'POST':
        # Tenta obter os dados JSON da requisição
        data = request.get_json()
        
        # Verifica se os dados JSON foram recebidos e se contêm 'usuario' e 'senha'
        if not data:
            logging.warning("Tentativa de login sem dados JSON.")
            return jsonify({'msg': 'Dados de login ausentes'}), 400

        # O HTML envia 'usuario' para o campo de usuário
        input_username = data.get('usuario') 
        senha = data.get('senha')

        # Verifica se 'usuario' e 'senha' foram fornecidos
        if not input_username or not senha:
            logging.warning(f"Tentativa de login com credenciais incompletas: usuario={input_username}, senha={'*' * len(senha) if senha else 'None'}")
            return jsonify({'msg': 'Nome de usuário e senha são obrigatórios'}), 400

        # Buscar o usuário no banco de dados pelo username (campo 'usuario' no modelo)
        user = Usuario.query.filter_by(usuario=input_username).first()
        logging.info(f"Tentativa de login para usuário: {input_username}. Usuário encontrado: {user is not None}")

        if not user:
            return jsonify({'msg': 'Usuário não existe'}), 401

        # Verificar se a senha fornecida corresponde ao hash armazenado no banco de dados
        if bcrypt.verify(senha, user.senha):
            # A identidade do token deve ser uma string
            access_token = create_access_token(identity=str(user.id)) 
            logging.info(f"Login bem-sucedido para usuário: {input_username}")
            return jsonify(access_token=access_token), 200
        else:
            logging.warning(f"Tentativa de login falhou para usuário {input_username}: senha incorreta.")
            return jsonify({'msg': 'Senha incorreta'}), 401

# Criar usuário
@usuario_bp.route('/usuario', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        usuario = data['usuario']
        nome = data['nome']
        email = data['email']
        senha = data['senha']

        # Hashear a senha
        hashed_password_str = bcrypt.hash(senha)
        
        new_user = Usuario(usuario=usuario, nome=nome, email=email, senha=hashed_password_str)
        db.session.add(new_user)
        db.session.commit()
        logging.info(f"Usuário criado: {usuario}")
        return jsonify({'message': 'user created'}), 201
    except KeyError as e:
        db.session.rollback()
        logging.error(f"Erro ao criar usuário (dados ausentes): {e}")
        return jsonify({'message': f'missing data: {e}'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao criar usuário: {e}")
        return jsonify({'message': 'error creating user'}), 500
            
# Rota para renderizar a página HTML protegida (NÃO REQUER JWT AQUI)
@usuario_bp.route('/protegido', methods=['GET'])
def render_protegido():
    return render_template('protegido.html')

# Rota da API que retorna dados protegidos (REQUER JWT)
@usuario_bp.route('/api/protegido', methods=['GET'])
@jwt_required()
def get_protected_data():
    current_user_id = get_jwt_identity()
    user = Usuario.query.get(current_user_id)
    if user:
        return jsonify({'message': f'Bem-vindo, {user.nome} (ID: {current_user_id})! Conteúdo protegido carregado com sucesso.'}), 200
    else:
        return jsonify({'message': 'Usuário não encontrado'}), 404

# Lista todos os usuários
@usuario_bp.route('/usuario', methods=['GET'])
def get_users():
    try:
        users = Usuario.query.all()
        return jsonify([usuario.json() for usuario in users]), 200
    except Exception as e:
        logging.error(f"Erro ao obter usuários: {e}")
        return jsonify({'message': 'error getting users'}), 500

# Atualizar usuário
@usuario_bp.route("/usuario/<int:id>", methods=["PUT"])
def update_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()
    if usuario_objeto:
        body = request.get_json()
        if body:
            try:
                if 'nome' in body:
                    usuario_objeto.nome = body['nome']
                if 'email' in body:
                    usuario_objeto.email = body['email']
                if 'senha' in body:
                    usuario_objeto.senha = bcrypt.hash(body['senha']) # Hashear a senha atualizada

                db.session.commit()
                logging.info(f"Usuário {id} atualizado.")
                return jsonify({'message': 'usuario updated successfully', 'usuario': usuario_objeto.json()}), 200
            except Exception as e:
                db.session.rollback()
                logging.error(f"Erro ao atualizar usuário {id}: {e}")
                return jsonify({'message': 'error updating user'}), 400
        else:
            return jsonify({'message': 'request body is empty'}), 400
    return jsonify({'message': 'user not found'}), 404

# Deletar usuário
from sqlalchemy.exc import IntegrityError # Exemplo para violação de integridade (chave estrangeira)

@usuario_bp.route('/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_usuario(id):
    try:
        id_usuario_logado = int(get_jwt_identity())

        # Permissão: apenas o próprio usuário pode se deletar
        if id != id_usuario_logado:
            return jsonify(msg='Você não tem permissão para deletar este usuário'), 403

        usuario_deletar = Usuario.query.get(id)
        if not usuario_deletar:
            return jsonify(msg='Usuário Não Encontrado'), 404

        # Deletar despesas e categorias associadas ao usuário (devido a CASCADE no modelo)
        # Se você configurou cascade="all, delete-orphan" nos relacionamentos,
        # a exclusão do usuário pode já cuidar disso automaticamente.
        # Caso contrário, as linhas abaixo são importantes.
        Despesa.query.filter_by(id_usuario=id).delete()
        Categoria.query.filter_by(id_usuario=id).delete()

        db.session.delete(usuario_deletar)
        db.session.commit()
        logging.info(f"Usuário {id} e dados relacionados deletados com sucesso.")
        return jsonify(msg='Usuário e todos os dados relacionados deletados com sucesso'), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao deletar usuário {id}: {e}")
        return jsonify(msg='Erro ao deletar usuário e despesas'), 500
