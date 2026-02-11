from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import database
import io
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)
   
def converter_transacao_para_json(tupla):
    return{
        "id": tupla[0],
        "data": tupla[1].strftime('%Y-%m-%d') if hasattr(tupla[1], 'strftime') else str(tupla[1]),
        "tipo": tupla[2],
        "categoria": tupla[3],
        "descricao": tupla[4],
        "valor": float(tupla[5])
    }

@app.route('/api/transacoes', methods=['GET'])
def listar_transacoes():
    try:
        conexao = database.criar_conexao()
        data_ini = request.args.get('inicio')
        data_fim = request.args.get('fim')

        if data_ini and data_fim:
            dados_brutos = database.busca_por_periodo(conexao, data_ini, data_fim)
        else:
            dados_brutos = database.listar_transacoes(conexao)

        conexao.close()

        list_json = [converter_transacao_para_json(t) for t in dados_brutos]
        return jsonify(list_json), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/transacoes', methods=['POST'])
def criar_transacao():
    try:
        novo_dado = request.get_json()

        categoria_id = novo_dado.get('categoria_id')
        descricao = novo_dado.get('descricao')
        valor = novo_dado.get('valor')

        if not categoria_id or not valor:
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400
        
        conexao = database.criar_conexao()
        database.adicionar_transacao(conexao, categoria_id, descricao, valor)
        conexao.close()

        return jsonify({"mensagem": "Sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/saldo', methods=['GET'])
def ver_saldo():
    conexao = database.criar_conexao()
    saldo, receitas, despesas = database.obter_saldo(conexao)
    conexao.close()

    return jsonify({
        "saldo": saldo,
        "total_receitas": receitas,
        "total_despesas": despesas
    })

@app.route('/api/categorias/<tipo>', methods=['GET'])
def listar_categorias(tipo):
    conexao = database.criar_conexao()
    categorias = database.listar_categoria_por_tipo(conexao, tipo)
    conexao.close()

    lista_formatada = [{"id": c[0], "nome": c[1]} for c in categorias]

    return jsonify(lista_formatada)

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def deletar_transacoes(id):
    try:
        conexao = database.criar_conexao()
        database.remover_transacao(conexao, id)
        conexao.close()

        return jsonify({"mensagem": "Transação removida com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/transacoes/<int:id>', methods=['PUT', 'PATCH'])
def editar_transacao(id):
    try:
        conexao = database.criar_conexao()

        tupla_antiga = database.buscar_transacao_por_id(conexao, id)

        if not tupla_antiga:
            conexao.close()
            return jsonify({"erro": "Transação não encontrada"}), 404
        
        desc_antiga = tupla_antiga[4]
        valor_antigo = float(tupla_antiga[5])
        cat_id_antiga = tupla_antiga[6]

        dados_novos = request.get_json() or {}

        nova_desc = dados_novos.get('descricao', desc_antiga)
        novo_valor = dados_novos.get('valor', valor_antigo)
        nova_cat_id = dados_novos.get('categoria_id', cat_id_antiga)

        database.atualizar_transacao(conexao,id,novo_valor,nova_desc,nova_cat_id)

        conexao.close()
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

@app.route('/api/grafico/despesas', methods=['GET'])
def dados_grafico():
    try:
        conexao = database.criar_conexao()
        dados = database.obter_dados_graficos(conexao)
        conexao.close()

        labels = [linha[0] for linha in dados]
        valores = [float(linha[1]) for linha in dados]

        return jsonify({
            "labels": labels,
            "valores": valores
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/exportar', methods=['GET'])
def baixar_relatorio():
    try:
        conexao = database.criar_conexao()

        sql = """
        SELECT t.id, t.data_criacao, c.tipo, c.nome as categoria, t.descricao, t.valor 
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        ORDER BY t.data_criacao DESC
        """
        df = pd.read_sql_query(sql, conexao)
        conexao.close()

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)