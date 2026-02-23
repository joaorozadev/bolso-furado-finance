from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/api/categorias', methods=['POST'])
@jwt_required()
def criar_categoria():
    try:
        usuario_atual_id = get_jwt_identity()
        dados = request.get_json()

        nome = dados.get('nome')
        tipo = dados.get('tipo')

        if not nome or not tipo:
            return jsonify({"erro": "Nome e tipo são obrigatórios"}), 400
        
        if tipo not in ['Receita', 'Despesa']:
            return jsonify({"erro": "O tipo deve ser 'Receita' ou 'Despesa'"}), 400

        conexao = database.criar_conexao()
        nova_categoria_id = database.adicionar_categoria(conexao, usuario_atual_id, nome, tipo)
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Categoria criada com sucesso!", "id": nova_categoria_id}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@categorias_bp.route('/api/categorias', methods=['GET'])
@jwt_required()
def listar_minhas_categorias():
    try:
        usuario_atual_id = get_jwt_identity()
        tipo_filtro = request.args.get('tipo')

        conexao = database.criar_conexao()
        dados_brutos = database.listar_categorias_usuario(conexao, usuario_atual_id, tipo_filtro)
        database.liberar_conexao(conexao)

        categorias_json = [
            {
                "id": c[0],
                "nome": c[1],
                "tipo": c[2],
                "is_default": c[3]
            } for c in dados_brutos
        ]

        return jsonify(categorias_json), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500