from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

contas_bp = Blueprint('contas', __name__)

@contas_bp.route('/api/contas', methods=['POST'])
@jwt_required()
def criar_conta():
    try:
        usuario_atual_id = get_jwt_identity()
        dados = request.get_json()

        nome = dados.get('nome')
        tipo = dados.get('tipo') 
        saldo_inicial = dados.get('saldo_inicial', 0.00)

        if not nome or not tipo:
            return jsonify({"erro": "Nome e tipo são obrigatórios"}), 400
        
        tipos_permitidos = ['Corrente', 'Poupança', 'Crédito', 'Dinheiro']
        if tipo not in tipos_permitidos:
            return jsonify({"erro": f"Tipo inválido. Escolha entre: {', '.join(tipos_permitidos)}"}), 400

        conexao = database.criar_conexao()
        nova_conta_id = database.adicionar_conta(conexao, usuario_atual_id, nome, tipo, saldo_inicial)
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Conta criada com sucesso!", "id": nova_conta_id}), 201
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@contas_bp.route('/api/contas', methods=['GET'])
@jwt_required()
def listar_minhas_contas():
    try:
        usuario_atual_id = get_jwt_identity()

        conexao = database.criar_conexao()
        dados_brutos = database.listar_contas(conexao, usuario_atual_id)
        database.liberar_conexao(conexao)

        contas_json = [
            {
                "id": c[0],
                "nome": c[1],
                "tipo": c[2],
                "saldo_inicial": float(c[3])
            } for c in dados_brutos
        ]

        return jsonify(contas_json), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500