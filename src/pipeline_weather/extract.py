
import requests
import json
from pathlib import Path
import os
import logging

from dotenv import load_dotenv

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Carrega as variáveis de ambiente
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / 'config' / '.env'

load_dotenv(ENV_FILE)


def extract_weather_data(url: str) -> dict:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("A resposta da API não está no formato JSON esperado.")

        if "main" not in data or "weather" not in data:
            raise ValueError("A resposta da API não contém os dados meteorológicos esperados.")

        if "id" not in data or "name" not in data:
            raise ValueError("A resposta da API não contém a identificação da cidade.")

        output_path = PROJECT_ROOT / 'data' / 'raw' / 'weather_data.json'
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logging.info("Arquivo salvo em %s", output_path)

        return data

    except requests.RequestException as error:
        logging.error("Erro ao conectar com a API: %s", error)
        raise

    except ValueError as error:
        logging.error("Erro ao interpretar a resposta JSON: %s", error)
        raise


def main():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    city = os.getenv('OPENWEATHER_CITY', 'São Paulo')
    country = os.getenv('OPENWEATHER_COUNTRY', 'BR')

    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY não configurada no config/.env")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city},{country}"
        f"&appid={api_key}"
        f"&units=metric"
        f"&lang=pt_br"
    )

    extract_weather_data(url)


if __name__ == "__main__":
    main()
