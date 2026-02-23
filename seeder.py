from faker import Faker
from app import database
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

def gerar_dados_falsos(quantidade=50, usuario_id=None):
    if not usuario_id:
        print('Erro: É obrigatório informar o ID do usuário')
        return
    print(f'Semeando o banco com {quantidade} transações')

    conexao = database.criar_conexao()
    if not conexao:
        print('Erro ao conectar ao banco.')
        return

    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT id, nome FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario:
            print(f'Erro: Usuário {usuario_id} não encontrado no banco')
            return
        
        print(f'Usuário encontrado: {usuario[1]}')

        cursor.execute("SELECT id FROM contas WHERE usuario_id = %s LIMIT 1", (usuario_id,))
        conta = cursor.fetchone()
        if not conta:
            print("Nenhuma conta encontrada. Criando uma 'Carteira Fake'...")
            cursor.execute(
                "INSERT INTO contas (usuario_id, nome, tipo, saldo_inicial) VALUES (%s, %s, %s, %s) RETURNING id",
                (usuario_id, "Carteira Fake", "Corrente", 0.0)
            )

            conta_id = cursor.fetchone()[0]
        else:
            conta_id = conta[0]
        
        cursor.execute('SELECT id FROM categorias WHERE is_default = TRUE OR usuario_id = %s', (usuario_id,))
        categorias_ids = [row[0] for row in cursor.fetchall()]

        if not categorias_ids:
            print('Erro: Nenhuma categoria encontrada no banco.')
            return
    
        sql= """
        INSERT INTO transacoes (usuario_id, conta_id, categoria_id, descricao, valor, data_criacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        for _ in range(quantidade):
            cat_id= random.choice(categorias_ids)
            descricao = fake.sentence(nb_words=3).replace('.','')
            valor = round(random.uniform(10.0, 750), 2)
            dias_atras = random.randint(0, 90)
            data_falsa = datetime.now() - timedelta(days=dias_atras)

            cursor.execute(sql, (usuario_id, conta_id, cat_id, descricao, valor, data_falsa))
        
        conexao.commit()

        print('Sucesso, dados falsos inseridos')

    except Exception as e:
        conexao.rollback()
        print(f'Erro ao semear o banco: {e}')
    finally:
        database.liberar_conexao(conexao)

if __name__ == '__main__':
    confirmacao = input("Isso vai inserir dados falsos no banco. Continuar? (s/n): ")
    if confirmacao.lower() == 's':
        u_id = input('Digite o ID do usuário que vai receber os dados: ')
        if not u_id.isdigit():
            print('ID inválido. Operação cancelada.')
        else:
            qtd = input("Quantas transações deseja criar? (Padrão: 50): ")
            qtd = int(qtd) if qtd.isdigit() else 50
            gerar_dados_falsos(qtd, int(u_id))
    else:
        print("Operação cancelada.")