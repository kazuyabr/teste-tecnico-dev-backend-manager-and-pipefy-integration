# Client Management & Pipefy Integration API

## Descrição

API desenvolvida em Python com FastAPI para gerenciar clientes e simular integração com o Pipefy via GraphQL, conforme teste técnico.

## Funcionalidades

- **Fluxo 1: Criação de Cliente e Mapeamento de Card**
  - Endpoint: POST `/api/v1/clientes`
  - Validação de dados de entrada
  - Persistência local em SQLite
  - Estruturação da mutation GraphQL para criação de card no Pipefy

- **Fluxo 2: Atualização de Card (Simulação de Webhook)**
  - Endpoint: POST `/api/v1/webhooks/pipefy/card-updated`
  - Verificação de idempotência usando event_id
  - Regra de negócio: prioridade alta para patrimônio >= 200.000
  - Estruturação das mutations GraphQL para atualização de status e prioridade no Pipefy
  - Atualização do banco local

## Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (validação)
- Uvicorn
- Python-dotenv
- Pytest

## Como Executar

### Pré-requisitos

- Python 3.8+
- pip

### Passos

1. Clone o repositório:
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd teste-tecnico-dev-backend-manager-and-pipefy-integration
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8001 --reload
   ```

5. Acesse a documentação:
   - Swagger UI: http://127.0.0.1:8001/docs
   - ReDoc: http://127.0.0.1:8001/redoc

## Exemplos de Requisições

### Criar um Cliente

```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/api/v1/clientes' \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

### Processar Webhook

```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/api/v1/webhooks/pipefy/card-updated' \
  -H 'Content-Type: application/json' \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

### Health Check

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/health'
```

## Estrutura do Projeto

```
app/
├── api/
│   └── endpoints.py          # Endpoints da API
├── db/
│   └── database.py           # Configuração do banco
├── models/
│   └── client.py             # Modelo SQLAlchemy
├── schemas/
│   └── client.py             # Schemas Pydantic
├── services/
│   └── client_service.py     # Lógica de negócio
├── pipefy_service.py         # Mutations GraphQL do Pipefy
└── tests/
    ├── test_client.py
    └── test_pipefy_service.py

main.py                       # Entrypoint
requirements.txt
```

## Testes

```bash
pytest
pytest --cov=app --cov-report=term-missing
pytest app/tests/test_client.py
```

## Prazo de Entrega

Desenvolver e enviar até 29 de Maio.

## Como Entregar

Preencher o formulário:
https://docs.google.com/forms/d/e/1FAIpQLSfRhrxW4B-2JGreNkrNCXlKJA9eCONGvL2JaRuQFelQz7PTkw/viewform
