# Pipeline ETL — Dados Climáticos de São Paulo

## Sobre o projeto

Este projeto implementa um pipeline ETL (Extract, Transform, Load) para coletar dados meteorológicos da cidade de São Paulo utilizando a API OpenWeatherMap.

Os dados são extraídos em formato JSON, tratados com Python e Pandas e armazenados em um banco de dados PostgreSQL. A execução das etapas é automatizada e orquestrada pelo Apache Airflow, utilizando Docker Compose.

## Arquitetura

O pipeline é dividido em três etapas:

1. **Extract:** consulta a API OpenWeatherMap e armazena os dados recebidos em JSON.
2. **Transform:** utiliza Pandas para normalizar, limpar e validar os dados meteorológicos.
3. **Load:** carrega os dados tratados no PostgreSQL, evitando duplicidade de observações.

O Apache Airflow coordena a execução das tarefas na seguinte sequência:

`Extract → Transform → Load`

## Tecnologias utilizadas

- Python 3.14
- UV
- Pandas
- Requests
- SQLAlchemy
- PostgreSQL
- Apache Airflow 3.1.7
- Docker e Docker Compose
- Pytest

## Estrutura do projeto

```text
pipeline_weather/
├── config/
├── dags/
│   └── weather_etl_pipeline.py
├── data/
│   ├── raw/
│   └── processed/
├── logs/
├── notebooks/
├── src/
│   └── pipeline_weather/
│       ├── database.py
│       ├── extract.py
│       ├── transform.py
│       └── load.py
├── tests/
├── docker-compose.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Pré-requisitos

- Python 3.12 ou superior
- Docker Desktop
- PostgreSQL 14 ou superior
- UV
- Chave de API do [OpenWeatherMap](https://openweathermap.org/api)

## Configuração do ambiente

Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
cd pipeline_weather
```

Instale as dependências:

```bash
uv sync --dev
```

Configure as variáveis de ambiente:

- Na raiz do projeto, crie o arquivo `.env` com a variável `AIRFLOW_UID`, utilizando o UID do seu usuário Linux. Consulte com `id -u`.
- Dentro de `config/`, crie o arquivo `.env` com a chave da API e as credenciais do PostgreSQL.

Não publique esses arquivos no GitHub.

## Executando o projeto

Com o Docker Desktop em execução, inicialize o ambiente Airflow:

```bash
docker compose up airflow-init
```

Depois, inicie os serviços:

```bash
docker compose up -d
```

Acesse a interface do Airflow:

http://localhost:8080

Credenciais padrão do ambiente local:

- Usuário: `airflow`
- Senha: `airflow`

Essas credenciais são destinadas exclusivamente ao ambiente local de desenvolvimento.

Ative a DAG `weather_etl_pipeline` e execute uma execução manual ou aguarde o agendamento automático, configurado para uma vez por hora.

## Executando os testes

Para executar os testes automatizados:

```bash
PYTHONPATH=src uv run pytest -v
```

## Banco de dados

Os dados meteorológicos são armazenados no PostgreSQL, no banco `weather_data`, na tabela `weather_observations`.

## Objetivo

Projeto desenvolvido para praticar conceitos de Engenharia de Dados, incluindo integração com APIs, processamento de dados, persistência em banco relacional, automação e orquestração de pipelines ETL.