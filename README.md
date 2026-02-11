# 💰 PyFinance-Tracker

> Um sistema híbrido de gestão financeira: Interface via Linha de Comando (CLI) para uso local e API RESTful pronta para conectar com Front-end Web.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

## 🎯 Objetivo do Projeto
Este projeto foi desenvolvido para consolidar conhecimentos em Back-end Moderno:
- **API RESTful** com Flask (Rotas, JSON, Verbos HTTP).
- **Integração SQL** pura com PostgreSQL e `psycopg2`.
- **Manipulação de Dados** (Pandas) e **Geração de Gráficos** (Matplotlib).
- **Boas Práticas:** Separação de responsabilidades (Database vs App), Tratamento de erros e CORS.

## 🛠️ Funcionalidades

### 🖥️ Versão Terminal (CLI)
- ✅ **CRUD Completo:** Gerenciamento via menus interativos.
- ✅ **Dashboards:** Geração de gráfico de pizza (Matplotlib) abrindo em janela nativa.
- ✅ **Relatórios:** Exportação local de CSV/Excel.

### 🌐 Versão Web (API)
- ✅ **Endpoints JSON:** Dados prontos para serem consumidos por React/Vue/Angular.
- ✅ **Filtros Avançados:** Busca por período (`?inicio=...&fim=...`).
- ✅ **Download via Stream:** Endpoint que gera e baixa o Excel sem salvar lixo no servidor.
- ✅ **População de Banco:** Script `seeder.py` para gerar dados falsos de teste automaticamente.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
Antes de começar, você precisa ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- Git

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/joaorozadev/bolso-furado-finance.git
cd bolso-furado-finance
```

### 2️⃣ Configurar o Ambiente Virtual (Recomendado)

```bash

#cria o ambiente virtual
python -m venv venv

# Ativa (Windows)
venv\Scripts\activate
# Ativa (Linux/Mac)
source venv/bin/activate

#instala os pacotes
pip install -r requirements.txt
```

### 3️⃣ Configurar o Banco de Dados

Crie um arquivo chamado `.env` na raiz do projeto e preencha com suas credenciais do PostgreSQL. O sistema criará a tabela automaticamente na primeira execução.

**Exemplo de conteúdo do arquivo `.env`:**

```ini
DB_NAME=nome_do_seu_banco
DB_USER=seu_usuario_postgres
DB_PASS=sua_senha_postgres
DB_HOST=localhost
DB_PORT=5432
```

### 4️⃣ Executar

Opção A: Rodar a API (Backend Web)
```bash
python app.py
# O servidor iniciará em [http://127.0.0.1:5000](http://127.0.0.1:5000)
```

Opção B: Rodar no Terminal (CLI)
```bash
python main.py
```

Opção C: Gerar dados de teste (Seeder)
```bash
python seeder.py
# Cria 50 transações fictícias para teste
```

## 🔌 Documentação da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/transacoes` | Lista todas as transações (ou filtra por data). |
| `POST` | `/api/transacoes` | Cria uma nova receita ou despesa. |
| `PUT` | `/api/transacoes/<id>` | Atualiza parcialmente uma transação. |
| `DELETE` | `/api/transacoes/<id>` | Remove uma transação. |
| `GET` | `/api/saldo` | Retorna saldo total, receitas e despesas. |
| `GET` | `/api/categorias/<tipo>` | Lista categorias (Receita ou Despesa). |
| `GET` | `/api/grafico/despesas` | Retorna JSON pronto para gráficos (Chart.js). |
| `GET` | `/api/exportar` | Baixa o relatório Excel automaticamente. |


---

## 🔮 Roadmap (Futuro do Projeto)

Pretendo evoluir nos estudos e atualizar este projeto para uma aplicação completa. Os próximos passos são:

* [x] **Fase 1: Base (Concluída)** - API REST, Database, CRUD e Scripts.
* [ ] **Fase 2: Front-end** - Criar interface visual consumindo a API.
* [ ] **Fase 3: Cloud** - Deploy no Render (API) e Neon (Banco).
* [ ] **Fase 4: IA** - Integração com LLM para auto-categorização de gastos.
