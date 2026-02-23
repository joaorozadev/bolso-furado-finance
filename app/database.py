import psycopg2
from psycopg2 import pool
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

pg_pool = None


# CONEXÃO COM O BANCO DE DADOS

def iniciar_pool():
    global pg_pool
    try:
        url = os.getenv("DATABASE_URL")
        
        if not url:
            print("Erro: A variável DATABASE_URL não foi encontrada no .env")
            return
        pg_pool = pool.ThreadedConnectionPool(1, 20, url)
        if pg_pool:
            print("Connection pool criada com sucesso!")
    except Exception as e:
            print(f'Erro ao criar pool: {e}')

def criar_conexao():
    global pg_pool
    try:
        if pg_pool is None:
            iniciar_pool()
            
        conn = pg_pool.getconn()
        return conn
    
    except Exception as e:
            print(f'Erro ao obter conexão do pool: {e}')
            return None

def liberar_conexao(conn):
    global pg_pool
    try:
        if pg_pool and conn:
            pg_pool.putconn(conn)
    except Exception as e:
        print(f'Erro ao devolver conexão {e}')



# CRIAÇÃO DAS TABELAS

def criar_tabela(conexao):
    cursor = conexao.cursor()

    # 1. Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL
    );            
    """)

    # 2. Tabela de Contas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        saldo_inicial NUMERIC(10, 2) DEFAULT 0.00,
        usuario_id INTEGER REFERENCES usuarios(id) NOT NULL
    );
    """)

    # 3. Tabela de Categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        tipo VARCHAR(10) CHECK (tipo IN ('Receita', 'Despesa')),
        usuario_id INTEGER REFERENCES usuarios(id),
        is_default BOOLEAN DEFAULT FALSE,
        UNIQUE(nome, tipo, usuario_id) 
    );
    """)

    # Popula categorias padrão se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        print("Criando categorias padrão...")
        dados = [
                ('Salário', 'Receita'), ('Freelance / Extra', 'Receita'),
                ('Retorno de Investimento', 'Receita'), ('Presente / Doação', 'Receita'),
                ('Educação', 'Receita'), ('Outras Receitas', 'Receita'),
                ('Transferência (Entrada)', 'Receita'), 
                ('Alimentação', 'Despesa'), ('Transporte', 'Despesa'),
                ('Moradia (Aluguel/Condomínio)', 'Despesa'), ('Contas (Luz/Água/Internet)', 'Despesa'),
                ('Assinaturas', 'Despesa'), ('Lazer', 'Despesa'),
                ('Educação', 'Despesa'), ('Saúde', 'Despesa'),
                ('Outras Despesas', 'Despesa'), ('Transferência (Saída)', 'Despesa')
            ]
        sql_insert = "INSERT INTO categorias (nome, tipo) VALUES (%s, %s)"
        cursor.executemany(sql_insert, dados)
        # Atualiza as do sistema para default
        cursor.execute("UPDATE categorias SET is_default = TRUE WHERE usuario_id IS NULL")
        print('Categorias inseridas com sucesso!')

    # 4. Tabela de Transações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id SERIAL PRIMARY KEY,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descricao TEXT,
        valor NUMERIC(10, 2) NOT NULL,
        categoria_id INTEGER REFERENCES categorias(id) NOT NULL,
        conta_id INTEGER REFERENCES contas(id) NOT NULL,
        usuario_id INTEGER REFERENCES usuarios(id) NOT NULL          
    );               
    """)

    # 5. Tabela de Metas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metas (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER REFERENCES usuarios(id) NOT NULL,
        categoria_id INTEGER REFERENCES categorias(id),
        valor_limite NUMERIC(10, 2) NOT NULL,
        mes_ano VARCHAR(7) NOT NULL,
        UNIQUE (usuario_id, categoria_id, mes_ano)
    );
    """)

    conexao.commit()


# USUÁRIOS E PERFIL

def cadastrar_usuario(conn, nome, email, senha_hash):
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome, email, senha_hash))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    
def buscar_usuario_por_email(conn, email):
    cursor = conn.cursor()
    sql ="SELECT id, nome, senha_hash FROM usuarios WHERE email = %s"
    cursor.execute(sql,( email,))
    return cursor.fetchone()

def obter_perfil(conn, usuario_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (usuario_id,))
    return cursor.fetchone()

def atualizar_perfil(conn, usuario_id, nome, email):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET nome = %s, email = %s WHERE id = %s", (nome, email, usuario_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    
def excluir_usuario_completo(conn, usuario_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacoes WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("DELETE FROM metas WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("DELETE FROM contas WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("DELETE FROM categorias WHERE usuario_id = %s AND is_default = FALSE", (usuario_id,))
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e



# CONTAS

def adicionar_conta(conn, usuario_id, nome, tipo, saldo_inicial):
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO contas (usuario_id, nome, tipo, saldo_inicial)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(sql,(usuario_id, nome, tipo, saldo_inicial))
        nova_conta_id = cursor.fetchone()[0]
        conn.commit()
        return nova_conta_id
    except Exception as e:
        conn.rollback()
        raise e

def listar_contas(conn, usuario_id):
    cursor = conn.cursor()
    sql = """
    SELECT id, nome, tipo, saldo_inicial
    FROM contas
    WHERE usuario_id = %s
    ORDER BY id ASC
    """
    cursor.execute(sql,(usuario_id,))
    return cursor.fetchall()


# CATEGORIAS

def adicionar_categoria(conn, usuario_id, nome, tipo):
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO categorias (usuario_id, nome, tipo)
        VALUES (%s, %s, %s) RETURNING id;
        """
        cursor.execute(sql, (usuario_id, nome, tipo))
        nova_categoria_id = cursor.fetchone()[0]
        conn.commit()
        return nova_categoria_id
    except Exception as e:
        conn.rollback()
        raise e
    
def listar_categorias_usuario(conn, usuario_id, tipo_filtro=None):
    cursor = conn.cursor()
    if tipo_filtro:
        sql = """
        SELECT id, nome, tipo, is_default
        FROM categorias
        WHERE (is_default = TRUE or usuario_id = %s) AND tipo = %s
        ORDER BY nome ASC
        """
        cursor.execute(sql, (usuario_id, tipo_filtro))
    else:    
        sql = """
        SELECT id, nome, tipo, is_default
        FROM categorias
        WHERE is_default = TRUE or usuario_id = %s
        ORDER BY nome ASC
        """
        cursor.execute(sql, (usuario_id,))
    return cursor.fetchall()

def listar_categoria_por_tipo(conn, tipo_filtro):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM categorias WHERE tipo = %s AND is_default = TRUE ORDER BY nome", (tipo_filtro,))
    return cursor.fetchall()


# TRANSAÇÕES E TRANSFERÊNCIAS

def adicionar_transacao(conn, usuario_id, conta_id, categoria_id, descricao, valor):
    cursor = conn.cursor()
    sql = """
    INSERT INTO transacoes (usuario_id, conta_id, categoria_id, descricao, valor)
    VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, (usuario_id, conta_id, categoria_id, descricao, valor))
        conn.commit()
    except Exception as e:
      conn.rollback()
      raise e

def listar_transacoes(conn, usuario_id):
    cursor = conn.cursor()
    query = """
    SELECT 
        t.id, t.data_criacao, c.tipo, c.nome as categoria, t.descricao, t.valor, 
        c.id as cat_id, ct.nome as conta_nome, ct.id as conta_id
    FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    JOIN contas ct ON t.conta_id = ct.id
    WHERE t.usuario_id = %s
    ORDER BY t.data_criacao DESC
    """
    cursor.execute(query, (usuario_id,))
    return cursor.fetchall()

def buscar_transacao_por_id(conn, id_transacao, usuario_id):
    cursor = conn.cursor()
    sql = """
    SELECT t.id, t.data_criacao, c.tipo, c.nome, t.descricao, t.valor, t.categoria_id
    FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.id = %s AND t.usuario_id = %s
    """
    cursor.execute(sql, (id_transacao, usuario_id))
    return cursor.fetchone()

def remover_transacao(conn, id_transacao, usuario_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacoes WHERE id = %s AND usuario_id = %s", (id_transacao, usuario_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def atualizar_transacao(conn, id_transacao, novo_valor, nova_desc, nova_cat_id, usuario_id):
    cursor = conn.cursor()
    try:
        query = """
        UPDATE transacoes
        SET valor = %s, descricao = %s, categoria_id = %s
        WHERE id = %s AND usuario_id = %s
        """
        cursor.execute(query, (novo_valor, nova_desc, nova_cat_id, id_transacao, usuario_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def busca_por_periodo(conn, usuario_id, data_inicio, data_fim):
    cursor = conn.cursor()
    sql = """
    SELECT 
        t.id, t.data_criacao, c.tipo, c.nome as categoria, t.descricao, t.valor, 
        c.id as cat_id, ct.nome as conta_nome, ct.id as conta_id
    FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    JOIN contas ct ON t.conta_id = ct.id
    WHERE t.usuario_id = %s AND t.data_criacao::date BETWEEN %s AND %s
    ORDER BY t.data_criacao ASC
    """
    cursor.execute(sql, (usuario_id, data_inicio, data_fim))
    return cursor.fetchall()

def obter_tipo_transacao(conn, id_transacao):
    cursor = conn.cursor()
    sql = """
    SELECT c.tipo FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.id = %s
    """
    cursor.execute(sql,(id_transacao,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def realizar_transferencia(conn, usuario_id, conta_origem_id, conta_destino_id, valor, descricao="Transferência"):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM categorias WHERE nome = 'Transferência (Saída)' AND is_default = TRUE")
        cat_saida_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM categorias WHERE nome = 'Transferência (Entrada)' AND is_default = TRUE")
        cat_entrada_id = cursor.fetchone()[0]

        sql_saida = "INSERT INTO transacoes (usuario_id, conta_id, categoria_id, descricao, valor) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_saida, (usuario_id, conta_origem_id, cat_saida_id, descricao, valor))
        
        sql_entrada = "INSERT INTO transacoes (usuario_id, conta_id, categoria_id, descricao, valor) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_entrada, (usuario_id, conta_destino_id, cat_entrada_id, descricao, valor))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e


# METAS E RELATÓRIOS (DASHBOARD)

def adicionar_meta(conn, usuario_id, categoria_id, valor_limite, mes_ano):
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO metas (usuario_id, categoria_id, valor_limite, mes_ano)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(sql, (usuario_id, categoria_id, valor_limite, mes_ano))
        nova_meta_id = cursor.fetchone()[0]
        conn.commit()
        return nova_meta_id
    except Exception as e:
        conn.rollback()
        raise e
    
def listar_metas(conn, usuario_id, mes_ano):
    cursor = conn.cursor()
    sql = """
    SELECT m.id, m.valor_limite, m.mes_ano, c.id AS cat_id, c.nome AS cat_nome
    FROM metas m
    LEFT JOIN categorias c ON m.categoria_id = c.id
    WHERE m.usuario_id = %s AND m.mes_ano = %s
    ORDER BY c.nome ASC
    """
    cursor.execute(sql, (usuario_id, mes_ano))
    return cursor.fetchall()

def obter_resumo_mes(conn, usuario_id, mes_ano):
    cursor = conn.cursor()
    sql = """
    SELECT 
        COALESCE(SUM(CASE WHEN c.tipo = 'Receita' THEN t.valor ELSE 0 END), 0) AS total_receitas,
        COALESCE(SUM(CASE WHEN c.tipo = 'Despesa' THEN t.valor ELSE 0 END), 0) AS total_despesas
    FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.usuario_id = %s AND TO_CHAR(t.data_criacao, 'YYYY-MM') = %s
    """
    cursor.execute(sql, (usuario_id, mes_ano))
    resultado = cursor.fetchone()
    
    receitas = float(resultado[0])
    despesas = float(resultado[1])
    return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}

def obter_dados_graficos(conn, usuario_id): 
    cursor = conn.cursor()
    sql = """
    SELECT c.nome, SUM(t.valor) 
    FROM transacoes t 
    JOIN categorias c ON t.categoria_id = c.id
    WHERE c.tipo = 'Despesa' AND t.usuario_id = %s
    GROUP BY c.nome
    """
    cursor.execute(sql, (usuario_id,))
    return cursor.fetchall()

def obter_gastos_por_categoria_mes(conn, usuario_id, mes_ano):
    cursor = conn.cursor()
    sql = """
    SELECT c.nome, SUM(t.valor) AS total
    FROM transacoes t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.usuario_id = %s AND c.tipo = 'Despesa' AND TO_CHAR(t.data_criacao, 'YYYY-MM') = %s
    GROUP BY c.nome
    ORDER BY total DESC
    """
    cursor.execute(sql, (usuario_id, mes_ano))
    return [{"categoria": linha[0], "total": float(linha[1])} for linha in cursor.fetchall()]

def obter_alertas_metas(conn, usuario_id, mes_ano):
    cursor = conn.cursor()
    alertas = []

    sql_categorias = """
    WITH gastos AS (
        SELECT categoria_id, SUM(valor) as total
        FROM transacoes
        WHERE usuario_id = %(u_id)s AND TO_CHAR(data_criacao, 'YYYY-MM') = %(m_ano)s
        GROUP BY categoria_id
    )
    SELECT c.nome, m.valor_limite, COALESCE(g.total, 0) AS valor_gasto
    FROM metas m
    JOIN categorias c ON m.categoria_id = c.id
    LEFT JOIN gastos g ON g.categoria_id = m.categoria_id
    WHERE m.usuario_id = %(u_id)s AND m.mes_ano = %(m_ano)s AND m.categoria_id IS NOT NULL
    """
    cursor.execute(sql_categorias, {'u_id': usuario_id, 'm_ano': mes_ano})
    
    for linha in cursor.fetchall():
        alertas.append({
            "categoria": linha[0],
            "limite": float(linha[1]),
            "gasto": float(linha[2])
        })

    sql_geral = """
    WITH gastos_gerais AS (
        SELECT SUM(t.valor) as total
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        WHERE t.usuario_id = %(u_id)s AND c.tipo = 'Despesa' AND TO_CHAR(t.data_criacao, 'YYYY-MM') = %(m_ano)s
    )
    SELECT m.valor_limite, COALESCE(g.total, 0) AS valor_gasto
    FROM metas m
    LEFT JOIN gastos_gerais g ON true
    WHERE m.usuario_id = %(u_id)s AND m.mes_ano = %(m_ano)s AND m.categoria_id IS NULL
    """
    cursor.execute(sql_geral, {'u_id': usuario_id, 'm_ano': mes_ano})
    meta_geral = cursor.fetchone()
    
    if meta_geral:
        alertas.append({
            "categoria": "Meta Geral do Mês",
            "limite": float(meta_geral[0]),
            "gasto": float(meta_geral[1])
        })

    return alertas