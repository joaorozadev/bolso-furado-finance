from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity 
from app import database
import pandas as pd
import io

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/api/grafico/despesas', methods=['GET'])
@jwt_required()
def dados_grafico():
    try:
        usuario_atual_id = get_jwt_identity() 
        conexao = database.criar_conexao()
        
        dados = database.obter_dados_graficos(conexao, usuario_atual_id) 
        database.liberar_conexao(conexao)

        labels = [linha[0] for linha in dados]
        valores = [float(linha[1]) for linha in dados]

        return jsonify({
            "labels": labels,
            "valores": valores
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@relatorios_bp.route('/api/exportar', methods=['GET'])
@jwt_required()
def baixar_relatorio():
    try:
        usuario_atual_id = get_jwt_identity() 
        conexao = database.criar_conexao()

        sql = """
        SELECT t.id, t.data_criacao, c.tipo, c.nome as categoria, t.descricao, t.valor 
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        WHERE t.usuario_id = %(u_id)s
        ORDER BY t.data_criacao DESC
        """
        
        df = pd.read_sql_query(sql, conexao, params={'u_id': usuario_atual_id})
        database.liberar_conexao(conexao)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Extrato')

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='relatorio_bolso_furado.xlsx'
        )
    except Exception as e:        
        return jsonify({"erro": str(e)}), 500