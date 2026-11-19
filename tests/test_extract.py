
import pytest
import requests

from pipeline_weather import extract


@pytest.fixture
def valid_api_response():
    """Simula uma resposta válida da OpenWeatherMap."""
    return {
        "id": 3448439,
        "name": "São Paulo",
        "main": {
            "temp": 25.0,
            "humidity": 60,
        },
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "céu limpo",
                "icon": "01d",
            }
        ],
    }


def test_extract_weather_data_success(
    mocker, tmp_path, valid_api_response
):
    """Verifica a extração e o salvamento de uma resposta válida."""

    mock_response = mocker.Mock()
    mock_response.json.return_value = valid_api_response
    mock_response.raise_for_status.return_value = None

    mock_get = mocker.patch(
        "pipeline_weather.extract.requests.get",
        return_value=mock_response,
    )

    mocker.patch.object(extract, "PROJECT_ROOT", tmp_path)

    result = extract.extract_weather_data("https://api-ficticia.com/weather")

    output_file = (
        tmp_path / "data" / "raw" / "weather_data.json"
    )

    assert result == valid_api_response
    assert output_file.exists()
    assert mock_get.call_count == 1
    mock_get.assert_called_once_with(
        "https://api-ficticia.com/weather",
        timeout=30,
    )


def test_extract_weather_data_rejects_invalid_json_type(mocker):
    """Verifica se uma resposta que não é um dicionário é rejeitada."""

    mock_response = mocker.Mock()
    mock_response.json.return_value = ["resposta", "invalida"]

    mocker.patch(
        "pipeline_weather.extract.requests.get",
        return_value=mock_response,
    )

    with pytest.raises(ValueError, match="formato JSON esperado"):
        extract.extract_weather_data("https://api-ficticia.com/weather")


def test_extract_weather_data_rejects_missing_weather_fields(mocker):
    """Verifica se a ausência dos dados meteorológicos é identificada."""

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "id": 3448439,
        "name": "São Paulo",
    }

    mocker.patch(
        "pipeline_weather.extract.requests.get",
        return_value=mock_response,
    )

    with pytest.raises(ValueError, match="dados meteorológicos esperados"):
        extract.extract_weather_data("https://api-ficticia.com/weather")


def test_extract_weather_data_rejects_missing_city_identification(mocker):
    """Verifica se a identificação da cidade é obrigatória."""

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "main": {"temp": 25.0},
        "weather": [{"main": "Clear"}],
    }

    mocker.patch(
        "pipeline_weather.extract.requests.get",
        return_value=mock_response,
    )

    with pytest.raises(ValueError, match="identificação da cidade"):
        extract.extract_weather_data("https://api-ficticia.com/weather")


def test_extract_weather_data_handles_http_error(mocker):
    """Verifica se erros de requisição HTTP são propagados."""

    mocker.patch(
        "pipeline_weather.extract.requests.get",
        side_effect=requests.ConnectionError("Falha de conexão"),
    )

    with pytest.raises(requests.ConnectionError):
        extract.extract_weather_data("https://api-ficticia.com/weather")
