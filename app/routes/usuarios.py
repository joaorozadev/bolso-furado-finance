from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/api/usuarios/perfil', methods=['GET'])
@jwt_required()
def ver_perfil():
    try:
        usuario_atual_id = get_jwt_identity()
        conexao = database.criar_conexao()
        perfil = database.obter_perfil(conexao, usuario_atual_id)
        database.liberar_conexao(conexao)

        if perfil:
            return jsonify({"id": perfil[0], "nome": perfil[1], "email": perfil[2]}), 200
        
        return jsonify({"erro": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@usuarios_bp.route('/api/usuarios/perfil', methods=['PUT'])
@jwt_required()
def editar_perfil():
    try:
        usuario_atual_id = get_jwt_identity()
        dados = request.get_json()
        
        nome = dados.get('nome')
        email = dados.get('email')

        if not nome or not email:
            return jsonify({"erro": "Nome e e-mail são obrigatórios"}), 400

        conexao = database.criar_conexao()
        database.atualizar_perfil(conexao, usuario_atual_id, nome, email)
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Perfil atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar perfil. Talvez o e-mail já esteja em uso.", "detalhes": str(e)}), 500
    
@usuarios_bp.route('/api/usuarios/excluir', methods=['DELETE'])
@jwt_required()
def excluir_conta():
    try:
        usuario_atual_id = get_jwt_identity()
        conexao = database.criar_conexao()
        
        database.excluir_usuario_completo(conexao, usuario_atual_id)
        
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Conta e todos os dados foram apagados permanentemente."}), 200
    except Exception as e:
        return jsonify({"erro": "Erro ao excluir conta", "detalhes": str(e)}), 500