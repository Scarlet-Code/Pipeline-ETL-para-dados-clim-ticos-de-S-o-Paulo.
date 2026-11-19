
import pandas as pd
import pytest

from pipeline_weather import load


@pytest.fixture
def valid_weather_df():
    """Cria um DataFrame válido para simular a carga."""
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


def test_load_weather_data_success(mocker, valid_weather_df):
    """Verifica se os dados são carregados corretamente."""

    mock_engine = mocker.MagicMock()
    mock_connection = mocker.MagicMock()
    mock_result = mocker.MagicMock()

    mock_result.rowcount = 1

    mock_connection.execute.side_effect = [
        mock_result,
        mocker.MagicMock(scalar=mocker.Mock(return_value=10)),
    ]

    mock_engine.begin.return_value.__enter__.return_value = mock_connection

    mocker.patch(
        "pipeline_weather.load.get_engine",
        return_value=mock_engine,
    )

    total = load.load_weather_data(
        "weather_observations",
        valid_weather_df,
    )

    assert total == 10
    assert mock_connection.execute.call_count == 2
    mock_engine.dispose.assert_called_once()


def test_load_weather_data_rejects_empty_dataframe(mocker):
    """Verifica se um DataFrame vazio é rejeitado."""

    mock_get_engine = mocker.patch(
        "pipeline_weather.load.get_engine"
    )

    with pytest.raises(ValueError, match="DataFrame vazio"):
        load.load_weather_data(
            "weather_observations",
            pd.DataFrame(),
        )

    mock_get_engine.assert_not_called()


def test_load_weather_data_handles_database_error(
    mocker,
    valid_weather_df,
):
    """Verifica se erros do banco são propagados."""

    mock_engine = mocker.MagicMock()
    mock_connection = mocker.MagicMock()

    mock_connection.execute.side_effect = Exception(
        "Erro simulado no PostgreSQL"
    )

    mock_engine.begin.return_value.__enter__.return_value = mock_connection

    mocker.patch(
        "pipeline_weather.load.get_engine",
        return_value=mock_engine,
    )

    with pytest.raises(Exception, match="Erro simulado"):
        load.load_weather_data(
            "weather_observations",
            valid_weather_df,
        )

    mock_engine.dispose.assert_called_once()
