
import pandas as pd
from pathlib import Path
import json

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Caminhos do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

path_name = PROJECT_ROOT / 'data' / 'raw' / 'weather_data.json'

# Colunas que serão removidas
columns_names_to_drop = [
    'weather',
    'weather_icon',
    'sys.type'
]

# Colunas que serão renomeadas
columns_names_to_rename = {
    "base": "base",
    "visibility": "visibility",
    "dt": "datetime",
    "timezone": "timezone",
    "id": "city_id",
    "name": "city_name",
    "cod": "code",
    "coord.lon": "longitude",
    "coord.lat": "latitude",
    "main.temp": "temperature",
    "main.feels_like": "feels_like",
    "main.temp_min": "temp_min",
    "main.temp_max": "temp_max",
    "main.pressure": "pressure",
    "main.humidity": "humidity",
    "main.sea_level": "sea_level",
    "main.grnd_level": "grnd_level",
    "wind.speed": "wind_speed",
    "wind.deg": "wind_deg",
    "wind.gust": "wind_gust",
    "clouds.all": "clouds",
    "sys.id": "sys_id",
    "sys.country": "country",
    "sys.sunrise": "sunrise",
    "sys.sunset": "sunset",
    # Colunas meteorológicas normalizadas
    "weather_id": "weather_id",
    "weather_main": "weather_main",
    "weather_description": "weather_description"
}

# Colunas que serão convertidas para datetime
columns_to_normalize_datetime = [
    'datetime',
    'sunrise',
    'sunset'
]


def validate_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida a qualidade dos dados meteorológicos antes da carga.
    Interrompe o pipeline quando encontra dados inválidos.
    """

    logging.info("→ Iniciando validação dos dados...")

    if df.empty:
        raise ValueError("DataFrame vazio. Não existem dados para validar.")

    # Verifica a presença das colunas essenciais
    required_columns = [
        'city_id',
        'city_name',
        'datetime',
        'temperature',
        'humidity',
        'latitude',
        'longitude',
        'clouds'
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    # Verifica valores nulos nos campos essenciais
    null_columns = [
        column for column in required_columns
        if df[column].isnull().any()
    ]

    if null_columns:
        raise ValueError(
            f"Existem valores nulos nas colunas: {null_columns}"
        )

    # Verifica os limites dos dados meteorológicos
    validations = {
        'temperature': df['temperature'].between(-100, 70),
        'humidity': df['humidity'].between(0, 100),
        'latitude': df['latitude'].between(-90, 90),
        'longitude': df['longitude'].between(-180, 180),
        'clouds': df['clouds'].between(0, 100)
    }

    invalid_columns = [
        column for column, valid in validations.items()
        if not valid.all()
    ]

    if invalid_columns:
        raise ValueError(
            f"Valores fora dos limites permitidos: {invalid_columns}"
        )

    # Verifica observações duplicadas
    if df.duplicated(subset=['city_id', 'datetime']).any():
        raise ValueError(
            "Foram encontradas observações meteorológicas duplicadas."
        )

    logging.info("✓ Validação concluída. Dados aprovados!")

    return df


def create_dataframe(path_name: Path) -> pd.DataFrame:

    logging.info("→ Criando DataFrame do arquivo JSON...")

    path = path_name

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    df = pd.json_normalize(data)

    logging.info("✓ DataFrame criado com %s linha(s)", len(df))

    return df


def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:

    df_weather = pd.json_normalize(
        df['weather'].apply(lambda x: x[0])
    )

    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })

    df = pd.concat([df, df_weather], axis=1)

    logging.info(
        "✓ Coluna 'weather' normalizada - %s colunas",
        len(df.columns)
    )

    return df


def drop_columns(df, columns):
    logging.info(f"→ Removendo colunas: {columns}")
    df = df.drop(columns=columns, errors='ignore')
    logging.info(f"✓ Colunas removidas com sucesso")
    return df


def rename_columns(
    df: pd.DataFrame,
    columns_names: dict[str, str]
) -> pd.DataFrame:

    logging.info(
        "→ Renomeando %s colunas...",
        len(columns_names)
    )

    df = df.rename(columns=columns_names)

    logging.info("✓ Colunas renomeadas")

    return df


def normalize_datetime_columns(
    df: pd.DataFrame,
    columns_names: list[str]
) -> pd.DataFrame:

    logging.info(
        "→ Convertendo colunas para datetime: %s",
        columns_names
    )

    for name in columns_names:
        df[name] = pd.to_datetime(
            df[name],
            unit='s',
            utc=True
        ).dt.tz_convert('America/Sao_Paulo')

    logging.info("✓ Colunas convertidas para datetime")

    return df


def data_transformations() -> pd.DataFrame:

    print("\nIniciando transformações")

    df = create_dataframe(path_name)

    df = normalize_weather_columns(df)

    df = drop_columns(
        df,
        columns_names_to_drop
    )

    df = rename_columns(
        df,
        columns_names_to_rename
    )

    df = normalize_datetime_columns(
        df,
        columns_to_normalize_datetime
    )

    df = validate_weather_data(df)

    logging.info("✓ Transformações e validações concluídas")

    return df


if __name__ == "__main__":

    df = data_transformations()

    print("\nResultado final:")
    print(df.to_string(index=False))

    print("\nDimensões do DataFrame:", df.shape)

    print("\nColunas:")
    print(df.columns.tolist())
