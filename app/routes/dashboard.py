from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@jwt_required()
def obter_dashboard():
    try:
        usuario_atual_id = get_jwt_identity()
        
        mes_ano = request.args.get('mes_ano')
        
        if not mes_ano:
            return jsonify({"erro": "O parâmetro mes_ano é obrigatório na URL"}), 400

        conexao = database.criar_conexao()
        
        resumo = database.obter_resumo_mes(conexao, usuario_atual_id, mes_ano)
        
        grafico_despesas = database.obter_gastos_por_categoria_mes(conexao, usuario_atual_id, mes_ano)
        
        database.liberar_conexao(conexao)

        dados_dashboard = {
            "mes_referencia": mes_ano,
            "resumo": resumo,
            "grafico_despesas": grafico_despesas
        }

        return jsonify(dados_dashboard), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500