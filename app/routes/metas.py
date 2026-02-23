from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

metas_bp = Blueprint('metas', __name__)

@metas_bp.route('/api/metas', methods=['POST'])
@jwt_required()
def criar_meta():
    try:
        usuario_atual_id = get_jwt_identity()
        dados = request.get_json()

        categoria_id = categoria_id = dados.get('categoria_id') 
        valor_limite = dados.get('valor_limite')
        mes_ano = dados.get('mes_ano')

        if not valor_limite or not mes_ano:
            return jsonify({"erro": "Valor limite e mês/ano (ex: 2026-02) são obrigatórios"}), 400
        
        conexao = database.criar_conexao()
        nova_meta_id = database.adicionar_meta(conexao, usuario_atual_id, categoria_id, valor_limite, mes_ano)
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Meta criada com sucesso!", "id": nova_meta_id}), 201
    
    except Exception as e:
        return jsonify({"erro": "Erro ao criar meta. Verifique se já existe uma meta para esta categoria neste mês.", "detalhe": str(e)}), 500
    
@metas_bp.route('/api/metas', methods=['GET'])
@jwt_required()
def listar_minhas_metas():
    try:
        usuario_atual_id = get_jwt_identity()
        mes_ano = request.args.get('mes_ano') 

        if not mes_ano:
            return jsonify({"erro": "O parâmetro mes_ano é obrigatório na URL"}), 400

        conexao = database.criar_conexao()
        dados_brutos = database.listar_metas(conexao, usuario_atual_id, mes_ano)
        database.liberar_conexao(conexao)

        metas_json = [
            {
                "id": m[0],
                "valor_limite": float(m[1]),
                "mes_ano": m[2],
                "categoria_id": m[3],
                "categoria_nome": m[4] if m[4] else "Meta Geral do Mês" 
            } for m in dados_brutos
        ]

        return jsonify(metas_json), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500