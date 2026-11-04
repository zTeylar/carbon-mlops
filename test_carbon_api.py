from datetime import UTC, datetime
import json
from unittest.mock import patch
import pytest
import requests
import responses

from main import extract_carbon_intensity, get_carbon_intensity, save_carbon_intensity_to_json, ingest_carbon_intensity


@responses.activate
def test_carbon_intensity_api():
    url = "https://api.carbonintensity.org.uk/intensity"

    responses.add(
        responses.GET,
        url,
        json=
        {
            "data":[ {
                "from": "2024-06-01T00:00Z",
                "to": "2024-06-01T00:30Z",
                "intensity": {
                    "forecast": 180,
                    "actual": 130,
                    "index": "moderate"
                }
            }]
        },
        status=200
    )

    data = get_carbon_intensity()

    assert data["from"] == datetime(2024, 6, 1, 0, 0, tzinfo=UTC)
    assert data["to"] == datetime(2024, 6, 1, 0, 30, tzinfo=UTC)
    assert data["forecast"] == 180
    assert data["actual"] == 130
    assert data["index"] == "moderate"


@responses.activate
def test_carbon_intensity_api_bad_response():
    url = "https://api.carbonintensity.org.uk/intensity"

    responses.add(
        responses.GET,
        url,
        json={
            "error": {
                "code": "400 Bad Request",
                "message": "string"
            }
        },
        status=400
    )

    with pytest.raises(requests.exceptions.HTTPError):
        get_carbon_intensity()


@responses.activate
def test_carbon_intensity_api_failure():
    url = "https://api.carbonintensity.org.uk/intensity"

    responses.add(
        responses.GET,
        url,
        json={
            "error":{
                "code": "500 Internal Server Error",
                "message": "string"
                }
        },
        status=500
    )

    with pytest.raises(requests.exceptions.HTTPError):
        get_carbon_intensity()


@responses.activate
def test_carbon_intensity_api_timeout():
    url = "https://api.carbonintensity.org.uk/intensity"

    responses.add(
        responses.GET,
        url,
        body=requests.exceptions.Timeout()
    )

    with pytest.raises(requests.exceptions.Timeout):
        get_carbon_intensity()


def test_carbon_intensity_api_empty_response():
    with pytest.raises(ValueError):
        extract_carbon_intensity({"data": []})


def test_save_carbon_intensity_to_json(tmp_path):
    data = {
        "from": "2024-06-01T00:00:00Z",
        "to": "2024-06-01T00:30:00Z",
        "forecast": 180,
        "actual": 130,
        "index": "moderate"
    }

    filename = save_carbon_intensity_to_json(data, output_dir=tmp_path)

    assert filename.exists()

    with open(filename, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    print(loaded_data)
    assert loaded_data == data


def test_ingest_carbon_intensity():
    data = {
            "data":[ {
                "from": "2024-06-01T00:00Z",
                "to": "2024-06-01T00:30Z",
                "intensity": {
                    "forecast": 180,
                    "actual": 130,
                    "index": "moderate"
                }
            }]
        }

    with patch(
            "main.fetch_carbon_intensity_raw",
            return_value=data) as mock_fetch, \
         patch(
            "main.upload_carbon_intensity_to_s3_bucket",
            return_value="s3://mock-bucket/carbon-intensity/2024-06-01_00-00-00-000000.json") as mock_save:
        
        result = ingest_carbon_intensity()
        assert result == "s3://mock-bucket/carbon-intensity/2024-06-01_00-00-00-000000.json"
        mock_fetch.assert_called_once()
        mock_save.assert_called_once()
        mock_save.assert_called_once_with(data)




def test_ingest_carbon_intensity_fetch_failure():
    with patch(
        "main.fetch_carbon_intensity_raw",
        side_effect=requests.exceptions.RequestException("API unavailable"),
    ) as mock_fetch, patch(
        "main.upload_carbon_intensity_to_s3_bucket",
    ) as mock_save:

        with pytest.raises(requests.exceptions.RequestException, match="API unavailable"):
            ingest_carbon_intensity()

        mock_fetch.assert_called_once()
        mock_save.assert_not_called()