import database
import datetime

def entrada_numerica(mensagem):
    while True:
        valor = input(mensagem)
        valor_tratado = valor.replace(',', '.')
        try:
            return float(valor_tratado)
        except ValueError:
            print('Digite um numero válido, ex: 12.50 ou 12,50')    

def menu():

    conexao = database.criar_conexao()
    database.criar_tabela(conexao)

    if conexao is None:
        print('O programa não pode continuar sem conexão com o banco')
        print('Verifique se o PostgreSQL está ligado e se o arquivo .env está correto')
        return

    while True:
        print('\n--- Bolso furado v1 ---')
        print('1. Adicionar Receita')
        print('2. Adicionar Despesa')
        print('3. Ver Saldo Atual')
        print('4. Gerar Gráfico de Despesas')
        print('5. Extrato completo(ver IDs/ editar / excluir)')
        print('6. Gerar relatorio (arquivo CSV/Excel)')
        print('7. Busca por período')
        print('8. Sair')

        opcao = input('Escolha uma opção: ')

        if opcao =='1' or opcao =='2':
            try:
            
                tipo = 'Receita' if opcao == '1' else 'Despesa'

                print(f'\nNOVO REGISTRO : {tipo.upper()}')

                valor = entrada_numerica('Valor: R$ ')
                descricao = input('Descricao: ')
                categoria = selecionar_categoria(tipo)

                print(f'Categoria selecionada: {categoria}')

                tipo = 'Receita' if opcao == '1' else 'despesa'
                database.adicionar_transacao(conexao, tipo, categoria, descricao, valor)
            except ValueError:
                print('Digite um valor númerico válido.')
        
        elif opcao == '3':
            saldo, receitas, despesas = database.obter_saldo(conexao)
            print(f'\nEntradas: R$ {receitas:.2f}')
            print(f'Despesas: R$ {despesas:.2f}')
            print(f'Saldo: R$ {saldo:.2f}')

        elif opcao == '4':
            database.gerar_grafico_despesas(conexao)

        elif opcao == '5':
            transacoes = database.listar_transacoes(conexao)

            exibir_tabela_transacoes(transacoes)

            if transacoes:
                acao = input('\n Deseja (E)ditar, (R)emover ou (V)oltar?').upper()

                if acao == 'R':
                    try:
                        id_alvo = int(input('Digite o ID para remover: '))
                        database.remover_transacao(conexao, id_alvo)
                    except ValueError:
                        print('ID inválido')

                elif acao == 'E':
                    try:
                        id_alvo = int(input('Digite o id para editar: '))
                        tipo_real = database.obter_tipo_transacao(conexao, id_alvo)

                        if not tipo_real:
                            print('ID não encontrado. Operação cancelada')
                            continue
                        print(f'Editando uma: {tipo_real}')
                        print('   Novos dados   ')

                        novo_valor = entrada_numerica('Novo valor: ')
                        nova_desc = input('Nova descrição: ')
                            
                        nova_cat = selecionar_categoria(tipo_real)
                        database.atualizar_transacao(conexao, id_alvo, novo_valor, nova_desc, nova_cat)
                    except ValueError:
                        print('Dados inválidos')

        elif opcao == '6':
            database.exportar_relatorio(conexao)

        elif opcao == '7':
            print('  Extrato por período  ')
            data_ini_str = input('Data inicial (dd/mm/aaaa): ')
            data_fim_str = input('Data final (dd/mm/aaaa): ')

            try:
                dt_ini = datetime.strptime(data_ini_str, "%d/%m/%Y").date()
                dt_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()

                if dt_ini > dt_fim:
                    print('A data inicial é maior que a final, invertendo a ordem...')
                    dt_ini, dt_fim = dt_fim, dt_ini

                transacoes_filtradas = database.busca_por_periodo(conexao, dt_ini, dt_fim)

                exibir_tabela_transacoes(transacoes_filtradas)

                if transacoes_filtradas:
                    input('\nPressione ENTER para voltar ao menu')
                    
            except ValueError:
                print('Formato de data inválido! Use DIA/MES/ANO (ex: 01/01/2026)')

        elif opcao == '8':
            print('Saindo...')
            conexao.close()
            break

        else:
            print('Opção inválida')

def selecionar_categoria(tipo_transacao):
    
    if tipo_transacao == 'Receita': 
        categorias = {
        1: "Salário",
        2: "Freelance / Extra",
        3: "Retorno de investimento",
        4: "presente / doação",
        5: "Outras receitas",
        6: "Educação",
        }
    else:
        categorias = {
        1:'Alimentação',
        2:'Transporte',
        3:'Moradia (Aluguel/Condomínio)',
        4:'Contas (Luz/Água/Internet)',
        5:'Assinaturas', 
        6:'Lazer',
        7:'Educação',
        8:'Saúde',
        9:'Outras despesas'

        }

    print('\n Selecione a categoria ')
    for numero, nome in categorias.items():
        print(f'{numero}. {nome}')
    while True:
        try:
            escolha = int(input('Digite o número da categoria: '))
            if escolha in categorias:
                return categorias[escolha]
            else:
                print('Número inválido, tente novamente')
        except ValueError:
            print('Somente números são válidos')

def exibir_tabela_transacoes(transacoes):
    if not transacoes:
        print('\nNenhuma transação encontrada para os critérios selecionados')
        return
    print('   extrato   ')

    larg_cat = max([len(t[3]) for t in transacoes] + [9]) + 2
    larg_desc = max([len(t[4]) for t in transacoes] + [9]) + 2
    
    cabecalho = f'{'ID':<5} | {'DATA':<12} | {'TIPO':<10} | {'CATEGORIA':<{larg_cat}} | {'DESCRIÇÃO':<{larg_desc}} | {'VALOR':<10}'
    print('-' * len(cabecalho))
    print(cabecalho)
    print('-' * len(cabecalho))

    for t in transacoes:
        data_fmt = t[1].strftime('%d/%m/%Y') if hasattr(t[1], 'strftime') else str(t[1])[:10]
        print(f'{t[0]:<5} | {data_fmt:<12} | {t[2]:<10} | {t[3]:<{larg_cat}} | {t[4]:<{larg_desc}} | R${t[5]:<7.2f}')

if __name__ == '__main__':
    menu()