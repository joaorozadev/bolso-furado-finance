from faker import Faker
import database
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

def gerar_dados_falsos(quantidade=50):
    print(f'Semeando o banco com {quantidade} transações')

    conexao = database.criar_conexao()
    cursor = conexao.cursor()

    cursor.execute('SELECT id FROM categorias')
    categorias_ids = [row[0] for row in cursor.fetchall()]

    if not categorias_ids:
        print('Erro, nenhuma categoria encontrada. Rode o app.py primeiro para criar as tabelas')
        return
    
    sql= """
    INSERT INTO transacoes (categoria_id, descricao, valor, data_criacao)
    VALUES (%s, %s, %s, %s)
    """

    for _ in range(quantidade):
        cat_id= random.choice(categorias_ids)

        descricao = fake.sentence(nb_words=3).replace('.','')

        valor = round(random.uniform(10.0, 750), 2)

        dias_atras = random.randint(0, 90)
        data_falsa = datetime.now() - timedelta(days=dias_atras)

        cursor.execute(sql, (cat_id, descricao, valor, data_falsa))
    
    conexao.commit()
    conexao.close()

    print('Sucesso, dados falsos inseridos')

if __name__ == '__main__':
    confirmacao = input("Isso vai inserir dados falsos no banco. Continuar? (s/n): ")
    if confirmacao.lower() == 's':
        qtd = input("Quantas transações deseja criar? (Padrão: 50): ")
        qtd = int(qtd) if qtd.isdigit() else 50
        gerar_dados_falsos(qtd)
    else:
        print("Operação cancelada.")