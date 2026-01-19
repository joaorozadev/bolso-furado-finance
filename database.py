import psycopg2
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

def criar_conexao():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )     
        return conn
    except Exception as e:
            print(f' Erro de conexão: {e}')
            return None
    
def criar_tabela(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id SERIAL PRIMARY KEY,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tipo VARCHAR(20) NOT NULL,
        categoria VARCHAR(50),
        descricao TEXT,
        valor NUMERIC(10, 2) NOT NULL
        )
    """)
    conexao.commit()

def adicionar_transacao(conexao,tipo,categoria,descricao,valor):
    cursor = conexao.cursor()
    sql = """
    INSERT INTO transacoes (tipo, categoria, descricao, valor)
    VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, (tipo, categoria, descricao, valor))
        conexao.commit()
        print('Transação salva com sucesso')
    except Exception as e:
      print(f'Erro ao salvar{e}')
      conexao.rollback()

def obter_saldo(conn):
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE LOWER(tipo) = 'receita'")
        resultado_receitas = cursor.fetchone()[0]
        total_receitas =float(resultado_receitas) if resultado_receitas else 0.0

        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE LOWER(tipo) = 'despesa'")
        resultado_despesas = cursor.fetchone()[0]
        total_despesas =float(resultado_despesas) if resultado_despesas else 0.0

        saldo_final = total_receitas - total_despesas
        return saldo_final, total_receitas, total_despesas


def listar_transacoes(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_criacao, tipo, categoria, descricao, valor FROM transacoes ORDER BY id ASC")
    return cursor.fetchall()

def remover_transacao(conn, id_transacao):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM transacoes WHERE id = %s", (id_transacao,))
        if not cursor.fetchone():
            print('ID não encontrado')
            return
        cursor.execute("DELETE FROM transacoes WHERE id = %s",(id_transacao,))
        conn.commit()
        print('Transação removida com sucesso')
    except Exception as e:
        print(f'Erro ao remover: {e}')
        conn.rollback()

def atualizar_transacao(conn, id_transacao, novo_valor, nova_desc, nova_cat):
    cursor = conn.cursor()
    try:
        query = """
        UPDATE transacoes
        SET valor = %s, descricao = %s, categoria = %s
        WHERE id = %s
        """
        cursor.execute(query, (novo_valor, nova_desc, nova_cat, id_transacao))
        conn.commit()
        print('Transação atualizada com sucesso')
    except Exception as e:
        print(f'Erro ao atualizar: {e}')
        conn.rollback()

def exportar_relatorio(conexao):
    try:
        print('\n Gerando relatorio')

        query = "SELECT * FROM transacoes"
        df = pd.read_sql_query(query,conexao)

        if df.empty:
            print('Não há dados no banco de dados para exportar')
            return
        
        print(f'Dados carregados: {len(df)} registros encontrados')
        print('Como deseja salvar?')
        print('1. Arquivo CSV')
        print('2. Arquivo Excel (.xlsx)')

        opcao = input('Digite a opção: ')

        if opcao not in ['1', '2']:
            print('Opção inválida. Operação cancelada')
            return
        
        nome_base = input('Nome do arquivo (sem extensão): ').strip()
        if not nome_base:
            print('Nome inválido')
            return
        
        if opcao == '1':
            nome_final = f'{nome_base}.csv'
            df.to_csv(nome_final, index=False, sep=';', encoding='utf-8-sig')

        elif opcao == '2':
            nome_final = f'{nome_base}.xlsx'
            df.to_excel(nome_final, index=False, engine='openpyxl')
        
        print(f'Operação concluída! arquivo salvo como {nome_final}')
    except Exception as e:
        print('Erro ao exportar : {e}')

def obter_tipo_transacao(conn, id_transacao):
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM transacoes WHERE id = %s", (id_transacao,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]
    else:
        return None
    
def obter_dados_graficos(conn): #reutilizar futuramente para gasto por cat, ex'gastou X em alimentos'
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, SUM(valor) FROM transacoes WHERE tipo = 'despesa' GROUP BY categoria")
    return cursor.fetchall() 

def gerar_grafico_despesas(conexao):

    dados = obter_dados_graficos(conexao)

    if not dados:
        print('Não há dados suficientes para gerar o gráfico')
        return
    
    categorias = []
    valores = []

    for linha in dados: 
        categorias.append(linha[0])
        valores.append(linha[1])

    plt.figure(figsize=(8, 6))
    plt.pie(valores,labels = categorias, autopct='%1.1f%%', startangle=140)
    plt.title('Minhas despesas por categoria')

    print('Gerando gráfico...')
    plt.show()

def busca_por_periodo(conexao, data_inicio, data_fim):
    cursor = conexao.cursor()
    sql = """
    SELECT id, data_criacao, tipo, categoria, descricao, valor
    FROM transacoes
    WHERE data_criacao::date BETWEEN %s AND %s
    ORDER BY data_criacao ASC
"""
    cursor.execute(sql, (data_inicio, data_fim))
    return cursor.fetchall()


