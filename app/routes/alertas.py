from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import database

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.route('/api/alertas', methods=['GET'])
@jwt_required()
def verificar_alertas():
    try:
        usuario_atual_id = get_jwt_identity()
        mes_ano = request.args.get('mes_ano') # Ex: 2026-02

        if not mes_ano:
            return jsonify({"erro": "O parâmetro mes_ano é obrigatório."}), 400

        conexao = database.criar_conexao()
        dados_brutos = database.obter_alertas_metas(conexao, usuario_atual_id, mes_ano)
        database.liberar_conexao(conexao)

        resultado_alertas = []

        for item in dados_brutos:
            if isinstance(item, dict):
                categoria = item.get('categoria', 'Desconhecida')
                limite = item.get('limite', 0)
                gasto = item.get('gasto', 0)
            else:
                categoria = item[0]
                limite = float(item[1])
                gasto = float(item[2])
            
            percentual = (gasto / limite * 100) if limite > 0 else 0
            
            if percentual >= 100:
                status = "Estourado"
                cor = "vermelho"
            elif percentual >= 80:
                status = "Atenção"
                cor = "amarelo"
            else:
                status = "Tranquilo"
                cor = "verde"

            resultado_alertas.append({
                "categoria": categoria,
                "valor_limite": limite,
                "valor_gasto": gasto,
                "percentual_gasto": round(percentual, 1),
                "status": status,
                "cor_indicativa": cor,
                "saldo_restante": round(limite - gasto, 2)
            })

        return jsonify(resultado_alertas), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500