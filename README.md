# 💰 Bolso Furado v1.3

> Um sistema de gestão financeira pessoal transformado em um SaaS (Software as a Service) multi-usuário. API RESTful robusta, segura e pronta para o consumo de aplicações Web e Mobile.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

## 🎯 Objetivo do Projeto
Este projeto nasceu como uma aplicação de terminal (CLI) e evoluiu para uma Arquitetura Web Profissional. O foco foi consolidar conhecimentos avançados em Back-end:
- **Arquitetura Modular:** Uso de Flask Blueprints para separação de domínios (Auth, Usuários, Transações, Metas).
- **Segurança:** Autenticação via JWT (JSON Web Tokens) e proteção de rotas.
- **Banco de Dados Relacional:** Integração SQL com PostgreSQL, Connection Pooling e deleção em cascata (Efeito Dominó).
- **Inteligência de Negócio:** Sistema de Metas mensais com alertas automáticos (Verde, Amarelo, Vermelho) com base no percentual de gastos.

## 🛠️ Funcionalidades da API

- ✅ **Autenticação:** Cadastro, Login e gerenciamento seguro de perfil.
- ✅ **Múltiplas Contas:** Suporte a Carteira, Conta Corrente, Cartão e transferências internas entre elas (com `COMMIT` e `ROLLBACK`).
- ✅ **Motor Analítico (Dashboard):** Endpoint consolidado que processa saldo, receitas, despesas e gastos agrupados em tempo real.
- ✅ **Relatórios e Exportação:** Geração de relatórios Excel em memória (`BytesIO`) via Pandas, sem sobrecarregar o servidor.
- ✅ **População de Banco:** Script inteligente `seeder.py` que gera dados fictícios associados a um usuário específico para testes rápidos.

*Nota: A versão original em CLI (Terminal) foi preservada na pasta `versao_legado_cli/` para fins de histórico de desenvolvimento.*

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
Antes de começar, você precisa ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- Banco de dados PostgreSQL (Recomendado: Neon DB na nuvem)

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/joaorozadev/bolso-furado-finance.git
cd bolso-furado-finance
```

### 2️⃣ Configurar o Ambiente Virtual 

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

### 3️⃣ Configurar as Variáveis de ambiente

Crie um arquivo .env na raiz do projeto e preencha com a sua string de conexão (ex: Neon DB) e a chave secreta do JWT:

**Exemplo de conteúdo do arquivo `.env`:**

```ini
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco?sslmode=require
JWT_SECRET_KEY=sua_chave_secreta_super_segura_aqui
```

### 4️⃣ Executar

```bash
python run.py
# O servidor iniciará em [http://127.0.0.1:5000](http://127.0.0.1:5000)
```

Opcional: Gerar dados de teste (Seeder)
```bash
python seeder.py
# Gerar dados de teste para um usuario
```

## 🔌 Documentação Base da API

Todas as rotas (exceto /auth) exigem um cabeçalho Authorization: Bearer <SEU_TOKEN>

| Domínio | Rota Principal | Descrição |
| :--- | :--- | :--- |
| Auth | `POST /api/auth/login` | Gera o token JWT de acesso. |
| Usuários | `DELETE /api/usuarios/excluir` | Apaga o usuário e todos os dados em cascata. |
| Dashboard | `GET /api/dashboard?mes_ano=YYYY-MM` | Retorna o resumo do mês e gráfico de despesas. |
| Alertas | `GET /api/alertas?mes_ano=YYYY-MM` | Retorna o status das metas (Verde, Amarelo, Vermelho). |
| Transações | `GET, POST, PUT, DELETE /api/transacoes` | CRUD completo de movimentações financeiras. |
| Contas | `POST /api/transferencias` | Realiza transferência de valores entre contas. |
| Relatórios | `GET /api/exportar` | Baixa o relatório Excel (.xlsx) do usuário. |


---

## 🔮 Roadmap (Status Atual)

Pretendo evoluir nos estudos e atualizar este projeto para uma aplicação completa. Os próximos passos são:

* [x] **Fase 1: Back-end CLI** - Versão de terminal (Arquivada).
* [x] **Fase 2: Back-end SaaS** - API REST, JWT, Blueprints e PostgreSQL em Nuvem(neon).
* [ ] **Fase 3: Front-end (Em andamento)** - Criação da interface visual consumindo a API (HTML/CSS/JS).
* [ ] **Fase 4: Deploy** - Hospedagem da API no Render/Railway.

---

## 🔄 Histórico de Refatoração e Evolução Arquitetural (Changelog bolso_furado V1.3)

Este projeto passou por uma grande refatoração para se adequar aos padrões de mercado de uma API escalável. As principais mudanças técnicas incluíram:

* **Migração para Padrão MVC (com Flask Blueprints):** O código monolítico foi desmembrado. O arquivo principal agora atua apenas como *Factory*, enquanto a lógica de negócio foi isolada na pasta `app/routes/` (Controllers) e as queries SQL concentradas no `database.py` (Models).
* **Implementação de Connection Pooling:** Substituição de conexões isoladas e síncronas por um pool de conexões com `psycopg2.pool.ThreadedConnectionPool`. Isso permite que a API atenda múltiplas requisições simultâneas sem estourar o limite do banco de dados na nuvem.
* **Segurança e Proteção de Rotas:** Transição de um sistema local para uma arquitetura "Stateless" utilizando **JWT (JSON Web Tokens)**. Todas as rotas (exceto o login/registro) agora exigem validação de token em tempo real.
* **Exclusão em Cascata (Efeito Dominó):** Criação de lógicas transacionais complexas no banco (usando `BEGIN`, `COMMIT` e `ROLLBACK`) para garantir que a exclusão de um usuário apague todas as suas transações, metas e contas associadas, sem ferir as restrições de Chave Estrangeira (Foreign Keys).
* **Otimização de Memória com `BytesIO`:** A exportação de relatórios em Excel com a biblioteca `pandas` foi reescrita para rodar inteiramente em memória RAM (`io.BytesIO`). O arquivo é servido diretamente para o download do usuário, eliminando a criação de "arquivos lixo" no disco do futuro servidor web.
* **Seeder Multi-usuário:** O script gerador de dados falsos (`Faker`) foi atualizado para uma lógica relacional, respeitando as amarras da arquitetura multi-usuário (inserindo transações atreladas corretamente ao `conta_id` e `usuario_id`).
