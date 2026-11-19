
from sqlalchemy import text
from urllib.parse import quote_plus
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import logging

from pipeline_weather.database import get_engine
from pipeline_weather.transform import data_transformations


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Carrega as variáveis de ambiente
PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_path = PROJECT_ROOT / 'config' / '.env'

load_dotenv(env_path)

TABLE_NAME = 'weather_observations'



def load_weather_data(table_name: str, df: pd.DataFrame):
    """Carrega os dados meteorológicos no PostgreSQL sem duplicar observações."""

    if df.empty:
        raise ValueError("DataFrame vazio. Nenhum dado para carregar.")

    engine = get_engine()

    try:
        logging.info("→ Carregando dados na tabela %s...", table_name)

        # Converte os registros do DataFrame em dicionários.
        records = df.to_dict(orient="records")

        columns = list(df.columns)
        column_names = ", ".join(f'"{column}"' for column in columns)
        placeholders = ", ".join(f":{column}" for column in columns)

        insert_query = text(f"""
            INSERT INTO "{table_name}" ({column_names})
            VALUES ({placeholders})
            ON CONFLICT (city_id, datetime) DO NOTHING
        """)

        with engine.begin() as connection:
            result = connection.execute(insert_query, records)

            inserted_records = result.rowcount

            total_records = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar()

            logging.info(
                "✓ Registros inseridos nesta execução: %s",
                inserted_records
            )

            logging.info(
                "Total de registros na tabela: %s",
                total_records
            )

        return total_records

    except Exception:
        logging.exception("Erro ao carregar dados no PostgreSQL.")
        raise

    finally:
        engine.dispose()


def main():
    """Executa a transformação e a carga dos dados."""

    logging.info("Iniciando processo de carga...")

    df = data_transformations()

    load_weather_data(TABLE_NAME, df)

    logging.info("✓ Processo de carga finalizado!")


if __name__ == "__main__":
    main()
