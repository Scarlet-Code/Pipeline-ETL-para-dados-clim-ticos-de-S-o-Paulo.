
import os
from pathlib import Path
from urllib.parse import quote_plus
from sqlalchemy.engine import Engine

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


# Localiza e carrega as variáveis de ambiente
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "config" / ".env"

load_dotenv(ENV_FILE)


def get_database_url() -> URL:
    """Monta a URL de conexão com o PostgreSQL."""

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [variable for variable in required_variables if not os.getenv(variable)]

    if missing:
        raise ValueError(
            f"Variáveis de ambiente não configuradas: {', '.join(missing)}"
        )

    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )


def get_engine() -> Engine:
    """Cria o mecanismo de conexão com o PostgreSQL."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def test_connection() -> bool:
    """Testa a conexão com o banco de dados."""

    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("Conexão estabelecida com sucesso!")
            print(result.scalar())
            return True

    finally:
        engine.dispose()
