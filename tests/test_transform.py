
import pandas as pd
import pytest
import json
from pathlib import Path

from pipeline_weather import transform

from pipeline_weather.transform import validate_weather_data


@pytest.fixture
def valid_weather_df():
    """Cria um DataFrame válido para os testes."""
    return pd.DataFrame([
        {
            "city_id": 3448439,
            "city_name": "São Paulo",
            "datetime": pd.Timestamp(
                "2026-11-19 16:00:00",
                tz="America/Sao_Paulo"
            ),
            "temperature": 25.0,
            "humidity": 60,
            "latitude": -23.5475,
            "longitude": -46.6361,
            "clouds": 40,
        }
    ])


def test_validate_weather_data_accepts_valid_data(valid_weather_df):
    """Verifica se dados válidos são aprovados."""
    result = validate_weather_data(valid_weather_df)

    pd.testing.assert_frame_equal(result, valid_weather_df)


def test_validate_weather_data_rejects_empty_dataframe():
    """Verifica se um DataFrame vazio é rejeitado."""
    with pytest.raises(ValueError, match="DataFrame vazio"):
        validate_weather_data(pd.DataFrame())


def test_validate_weather_data_rejects_missing_column(valid_weather_df):
    """Verifica se uma coluna obrigatória ausente é identificada."""
    df = valid_weather_df.drop(columns=["city_name"])

    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        validate_weather_data(df)


def test_validate_weather_data_rejects_null_values(valid_weather_df):
    """Verifica se valores nulos nas colunas obrigatórias são rejeitados."""
    df = valid_weather_df.copy()
    df.loc[0, "humidity"] = None

    with pytest.raises(ValueError, match="valores nulos"):
        validate_weather_data(df)


def test_validate_weather_data_rejects_invalid_humidity(valid_weather_df):
    """Verifica se umidade fora do intervalo permitido é rejeitada."""
    df = valid_weather_df.copy()
    df.loc[0, "humidity"] = 150

    with pytest.raises(ValueError, match="fora dos limites"):
        validate_weather_data(df)


def test_validate_weather_data_rejects_invalid_temperature(valid_weather_df):
    """Verifica se temperatura fora do intervalo permitido é rejeitada."""
    df = valid_weather_df.copy()
    df.loc[0, "temperature"] = 100

    with pytest.raises(ValueError, match="fora dos limites"):
        validate_weather_data(df)


def test_validate_weather_data_rejects_duplicate_observations(valid_weather_df):
    """Verifica se observações duplicadas são rejeitadas."""
    df = pd.concat(
        [valid_weather_df, valid_weather_df],
        ignore_index=True
    )

    with pytest.raises(ValueError, match="duplicadas"):
        validate_weather_data(df)


def test_create_dataframe_success(tmp_path):
    """Verifica a criação de um DataFrame a partir de um JSON."""

    weather_data = {
        "name": "São Paulo",
        "id": 3448439,
        "main": {
            "temp": 25.0,
            "humidity": 60
        }
    }

    json_file = tmp_path / "weather_data.json"

    json_file.write_text(
        json.dumps(weather_data),
        encoding="utf-8"
    )

    df = transform.create_dataframe(json_file)

    assert len(df) == 1
    assert df.loc[0, "name"] == "São Paulo"
    assert df.loc[0, "id"] == 3448439
    assert df.loc[0, "main.temp"] == 25.0


def test_create_dataframe_file_not_found(tmp_path):
    """Verifica se a função rejeita arquivos inexistentes."""

    json_file = tmp_path / "arquivo_inexistente.json"

    with pytest.raises(FileNotFoundError):
        transform.create_dataframe(json_file)


def test_normalize_weather_columns():
    """Verifica a normalização da coluna weather."""

    df = pd.DataFrame({
        "name": ["São Paulo"],
        "weather": [[
            {
                "id": 800,
                "main": "Clear",
                "description": "céu limpo",
                "icon": "01d"
            }
        ]]
    })

    result = transform.normalize_weather_columns(df)

    assert result.loc[0, "weather_id"] == 800
    assert result.loc[0, "weather_main"] == "Clear"
    assert result.loc[0, "weather_description"] == "céu limpo"
    assert result.loc[0, "weather_icon"] == "01d"

    assert "weather" in result.columns


def test_drop_columns():
    df = pd.DataFrame({
        "city_name": ["São Paulo"],
        "weather": ["Clear"]
    })

    result = transform.drop_columns(df, ["weather"])

    assert "weather" not in result.columns
    assert "city_name" in result.columns


def test_rename_columns():
    df = pd.DataFrame({
        "name": ["São Paulo"],
        "main.temp": [25.0]
    })

    result = transform.rename_columns(
        df,
        {
            "name": "city_name",
            "main.temp": "temperature"
        }
    )

    assert "city_name" in result.columns
    assert "temperature" in result.columns
    assert result.loc[0, "city_name"] == "São Paulo"
    assert result.loc[0, "temperature"] == 25.0
