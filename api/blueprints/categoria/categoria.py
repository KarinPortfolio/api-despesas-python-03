from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Categoria

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categoria')

@categoria_bp.route('/nova', methods=['POST'])
@jwt_required()
def criar_categoria():
    try:
        id_usuario = int(get_jwt_identity())
        nova_categoria_data = request.get_json()

        if not nova_categoria_data or 'nome' not in nova_categoria_data:
            return jsonify({'msg': 'Dados Insuficientes (descrição da categoria é obrigatória)'}), 400

        categoria = Categoria(
            nome=nova_categoria_data['nome'],
            id_usuario=id_usuario # Associando a categoria ao usuário logado
        )

        db.session.add(categoria)
        db.session.commit()
        db.session.refresh(categoria)

        return jsonify({'msg': 'Categoria cadastrada Com Sucesso!', 'categoria': categoria.json()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar categoria: {str(e)}")
        return jsonify(msg='Erro ao cadastrar categoria'), 500

@categoria_bp.route('/atualizar/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_categoria(id):
    try:
        id_usuario = int(get_jwt_identity())
        categoria_atualizar = Categoria.query.filter_by(id=id, id_usuario=id_usuario).first()

        if not categoria_atualizar:
            return jsonify(msg='Categoria Não Encontrada!'), 404

        dados = request.get_json()
        if 'nome' in dados:
            categoria_atualizar.nome = dados['nome']

        db.session.commit()

        return jsonify({'msg': 'Categoria Atualizada Com Sucesso!', 'categoria': categoria_atualizar.json()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar categoria: {str(e)}")
        return jsonify(msg='Erro ao atualizar categoria'), 500

@categoria_bp.route('/listar')
@jwt_required()
def listar_categorias():
    try:
        id_usuario = int(get_jwt_identity())
        query = Categoria.query.filter_by(id_usuario=id_usuario)

        categoria_id_filtro = request.args.get('id')
        if categoria_id_filtro is not None:
            try:
                query = query.filter_by(id=int(categoria_id_filtro))
            except ValueError:
                return jsonify({'msg': 'ID de Categoria Inválido'}), 400

        categorias = query.all()
        if not categorias:
            return jsonify({'msg': 'Nenhuma categoria encontrada para este usuário!'}), 200

        return jsonify([categoria.json() for categoria in categorias]), 200
    except Exception as e:
        print(f"Erro ao listar categorias: {str(e)}")
        return jsonify(msg='Erro ao listar categorias'), 500

@categoria_bp.route('/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_categoria(id):
    try:
        id_usuario = int(get_jwt_identity())
        categoria_deletar = Categoria.query.filter_by(id=id, id_usuario=id_usuario).first()

        if not categoria_deletar:
            return jsonify(msg='Categoria Não Encontrada'), 404

        db.session.delete(categoria_deletar)
        db.session.commit()

        return jsonify(msg='Categoria deletada com sucesso'), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar categoria: {str(e)}")
        return jsonify(msg='Erro ao deletar categoria'), 500