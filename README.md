# 💰 PyFinance-Tracker

> Um gerenciador de finanças pessoais via linha de comando (CLI), desenvolvido para aplicar conceitos de manipulação de dados e bancos de dados relacionais.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

## 🎯 Objetivo do Projeto
Este projeto foi desenvolvido com o intuito de consolidar e testar meus conhecimentos em:
- **Lógica de Programação com Python**;
- **Integração com Banco de Dados (CRUD)** usando PostgreSQL e `psycopg2`;
- **Análise de Dados** e exportação de relatórios (Excel/CSV) com Pandas;
- **Visualização de Dados** gerando gráficos com Matplotlib.

## 🛠️ Funcionalidades
- ✅ **CRUD Completo:** Adicionar, editar e remover receitas e despesas.
- ✅ **Extrato Detalhado:** Visualização formatada de todas as transações.
- ✅ **Filtro por Período:** Busca inteligente de transações por intervalo de datas.
- ✅ **Dashboards:** Geração automática de gráfico de pizza (Despesas por Categoria).
- ✅ **Relatórios:** Exportação dos dados para planilhas Excel (`.xlsx`) e CSV.
- ✅ **Validação de Dados:** Sistema robusto para evitar erros de digitação do usuário.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
Antes de começar, você precisa ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- Git

### 1️⃣ Clonar o repositório
```bash
git clone [https://github.com/joaorozadev/bolso-furado-finance.git](https://github.com/joaorozadev/bolso-furado-finance.git)
cd bolso-furado-finance
```

### 1️⃣ Clonar o repositório
```bash
git clone [https://github.com/joaorozadev/bolso-furado-finance.git](https://github.com/joaorozadev/bolso-furado-finance.git)
cd bolso-furado-finance
```

### 2️⃣ Configurar o Ambiente Virtual (Recomendado)

```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3️⃣ Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar o Banco de Dados

Crie um arquivo chamado `.env` na raiz do projeto e preencha com suas credenciais do PostgreSQL. O sistema criará a tabela automaticamente na primeira execução.

**Exemplo de conteúdo do arquivo `.env`:**

```ini
DB_NAME=nome_do_seu_banco
DB_USER=seu_usuario_postgres
DB_PASS=sua_senha_postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5️⃣ Executar

```bash
python main.py
```

---

## 🔮 Roadmap (Futuro do Projeto)

Pretendo evoluir nos estudos e atualizar este projeto para uma aplicação completa. Os próximos passos são:

* [ ] **Front-end Web:** Criar uma interface visual amigável para sair do terminal.
* [ ] **Meta de Gastos:** Implementar alertas quando o usuário ultrapassar um teto de gastos.
* [ ] **Autenticação e Normalização:** Criar sistema de login para múltiplos usuários e realizar a normalização dos dados (tabelas relacionais).
