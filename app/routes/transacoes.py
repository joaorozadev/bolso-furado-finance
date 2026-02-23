from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import limiter
from app import database

transacoes_bp = Blueprint('transacoes', __name__)

def converter_transacao_para_json(t):
    return {
        "id": t[0],
        "data": t[1].strftime("%Y-%m-%d %H:%M:%S") if t[1] else None,
        "tipo": t[2],
        "categoria": t[3],
        "descricao": t[4],
        "valor": float(t[5]),
        "categoria_id": t[6],
        "conta_nome": t[7],
        "conta_id": t[8]
    }

@transacoes_bp.route('/api/transacoes', methods=['GET'])
@jwt_required()
def listar_transacoes():
    try:
        usuario_atual_id = get_jwt_identity()

        conexao = database.criar_conexao()
        data_ini = request.args.get('inicio')
        data_fim = request.args.get('fim')

        if data_ini and data_fim:
            dados_brutos = database.busca_por_periodo(conexao, usuario_atual_id, data_ini, data_fim)
        else:
            dados_brutos = database.listar_transacoes(conexao, usuario_atual_id)

        database.liberar_conexao(conexao)

        list_json = [converter_transacao_para_json(t) for t in dados_brutos]
        return jsonify(list_json), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@transacoes_bp.route('/api/transacoes', methods=['POST'])
@jwt_required()
def criar_transacao():
    try:
        usuario_atual_id = get_jwt_identity() 

        novo_dado = request.get_json()
        conta_id = novo_dado.get('conta_id')
        categoria_id = novo_dado.get('categoria_id')
        descricao = novo_dado.get('descricao')
        valor = novo_dado.get('valor')

        if not conta_id or not categoria_id or not valor:
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400
        
        conexao = database.criar_conexao()
        database.adicionar_transacao(
        conexao,
        usuario_atual_id, 
        conta_id, 
        categoria_id, 
        descricao, 
        valor
        )
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@transacoes_bp.route('/api/saldo', methods=['GET'])
@jwt_required() 
def ver_saldo():
    try:
        usuario_atual_id = get_jwt_identity()

        conexao = database.criar_conexao()
        saldo, receitas, despesas = database.obter_saldo(conexao, usuario_atual_id)
        database.liberar_conexao(conexao)

        return jsonify({
            "saldo": saldo,
            "total_receitas": receitas,
            "total_despesas": despesas
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@transacoes_bp.route('/api/transacoes/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_transacoes(id):
    try:
        usuario_atual_id = get_jwt_identity()

        conexao = database.criar_conexao()
        database.remover_transacao(conexao, id, usuario_atual_id)
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Transação removida com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@transacoes_bp.route('/api/transacoes/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def editar_transacao(id):
    try:
        usuario_atual_id = get_jwt_identity() 

        conexao = database.criar_conexao()
        
        tupla_antiga = database.buscar_transacao_por_id(conexao, id, usuario_atual_id)

        if not tupla_antiga:
            database.liberar_conexao(conexao)
            return jsonify({"erro": "Transação não encontrada ou acesso negado"}), 404
        
        desc_antiga = tupla_antiga[4]
        valor_antigo = float(tupla_antiga[5])
        cat_id_antiga = tupla_antiga[6]

        dados_novos = request.get_json() or {}

        nova_desc = dados_novos.get('descricao', desc_antiga)
        novo_valor = dados_novos.get('valor', valor_antigo)
        nova_cat_id = dados_novos.get('categoria_id', cat_id_antiga)

        database.atualizar_transacao(
        conexao, 
        id, 
        novo_valor, 
        nova_desc, 
        nova_cat_id, 
        usuario_atual_id
        )

        database.liberar_conexao(conexao)
        return jsonify({
            "mensagem": "Atualizado com sucesso!",
            "dados_finais": {
                "descricao": nova_desc,
                "valor": novo_valor,
                "categoria_id": nova_cat_id
            }
        }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500