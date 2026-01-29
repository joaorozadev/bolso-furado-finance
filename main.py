import database
from datetime import datetime as dt_class

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

    if conexao is None:
        print('O programa não pode continuar sem conexão com o banco')
        print('Verifique se o PostgreSQL está ligado e se o arquivo .env está correto')
        return
    
    database.criar_tabela(conexao)

    while True:
        print('\n--- Bolso furado v1.1 (Normalizado) ---')
        print('1. Adicionar Receita')
        print('2. Adicionar Despesa')
        print('3. Ver Saldo Atual')
        print('4. Gerar Gráfico de Despesas')
        print('5. Extrato completo(Editar / Excluir)')
        print('6. Gerar relatorio (CSV/Excel)')
        print('7. Busca por período')
        print('8. Sair')

        opcao = input('Escolha uma opção: ')

        if opcao =='1' or opcao =='2':
            try:
                tipo = 'Receita' if opcao == '1' else 'Despesa'
                print(f'\nNOVO REGISTRO : {tipo.upper()}')

                valor = entrada_numerica('Valor: R$ ')
                descricao = input('Descricao: ')
                id_categoria = selecionar_categoria(conexao, tipo)

                if id_categoria:
                    database.adicionar_transacao(conexao, id_categoria, descricao, valor)
                else:
                    print('Operação cancelada, nenhuma categoria selecionada')

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
                            
                        nova_cat_id = selecionar_categoria(conexao, tipo_real)

                        if nova_cat_id:
                            database.atualizar_transacao(conexao, id_alvo, novo_valor, nova_desc, nova_cat_id)
                    except ValueError:
                        print('Dados inválidos')

        elif opcao == '6':
            database.exportar_relatorio(conexao)

        elif opcao == '7':
            print('  Extrato por período  ')
            data_ini_str = input('Data inicial (dd/mm/aaaa): ')
            data_fim_str = input('Data final (dd/mm/aaaa): ')

            try:
                dt_ini = dt_class.strptime(data_ini_str, "%d/%m/%Y").date()
                dt_fim = dt_class.strptime(data_fim_str, "%d/%m/%Y").date()

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

def selecionar_categoria(conexao, tipo_transacao):
    
    opcoes = database.listar_categoria_por_tipo(conexao, tipo_transacao)
    if not opcoes:
        print(f'Nenhuma categoria de {tipo_transacao} encontrada')
        return None
    
    print('\n Selecione a categoria ')

    for i, (id_real, nome) in enumerate(opcoes, start=1):
        print(f'{i}. {nome}')

    while True:
        try:
            escolha = int(input('Digite o número da categoria: '))
            if 1 <= escolha <= len(opcoes):
                categoria_selecionada = opcoes[escolha - 1]
                id_real_banco = categoria_selecionada[0]
                print(f'Selecionado:{categoria_selecionada[1]}')
                return id_real_banco
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
    
    cabecalho = f"{'ID':<5} | {'DATA':<12} | {'TIPO':<10} | {'CATEGORIA':<{larg_cat}} | {'DESCRIÇÃO':<{larg_desc}} | {'VALOR':<10}"
    divisoria = '-' *len(cabecalho)
    print(divisoria)
    print(cabecalho)
    print(divisoria)

    for t in transacoes:
        data_show = t[1]
        if hasattr(data_show, 'strftime'):
            data_str = data_show.strftime('%d/%m/%Y')
        else:
            data_str = str(data_show)[:10]

        print(f'{t[0]:<5} | {data_str:<12} | {t[2]:<10} | {t[3]:<{larg_cat}} | {t[4]:<{larg_desc}} | R${t[5]:<7.2f}')
    print(divisoria)

if __name__ == '__main__':
    menu()
