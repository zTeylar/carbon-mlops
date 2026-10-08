from datetime import datetime, timezone
import pytest
import requests
import responses
from main import get_carbon_intensity, extract_carbon_intensity


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

    assert data["from"] == datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    assert data["to"] == datetime(2024, 6, 1, 0, 30, tzinfo=timezone.utc)
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