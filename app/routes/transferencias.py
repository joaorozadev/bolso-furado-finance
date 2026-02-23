from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

transferencias_bp = Blueprint('transferencias', __name__)

@transferencias_bp.route('/api/transferencias', methods=['POST'])
@jwt_required()
def transferir():
    try:
        usuario_atual_id = get_jwt_identity()
        dados = request.get_json()

        conta_origem_id = dados.get('conta_origem_id')
        conta_destino_id = dados.get('conta_destino_id')
        valor = dados.get('valor')
        descricao = dados.get('descricao', 'Transferência entre contas')

        if not conta_origem_id or not conta_destino_id or not valor:
            return jsonify({"erro": "Conta de origem, conta de destino e valor são obrigatórios."}), 400
        
        if conta_origem_id == conta_destino_id:
            return jsonify({"erro": "A conta de origem e destino não podem ser a mesma."}), 400
        
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                return jsonify({"erro": "O valor da transferência deve ser maior que zero."}), 400
        except ValueError:
            return jsonify({"erro": "Valor inválido."}), 400

        conexao = database.criar_conexao()

        database.realizar_transferencia(
            conexao, 
            usuario_atual_id, 
            conta_origem_id, 
            conta_destino_id, 
            valor_float, 
            descricao
        )
        
        database.liberar_conexao(conexao)

        return jsonify({"mensagem": "Transferência realizada com sucesso!"}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500