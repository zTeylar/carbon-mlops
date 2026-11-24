from datetime import UTC, datetime
import json
from unittest.mock import patch
import pytest
import requests
import responses
from pydantic import ValidationError

from main import extract_carbon_intensity, get_carbon_intensity, save_carbon_intensity_to_json, ingest_carbon_intensity


@responses.activate
def test_carbon_intensity_api(valid_payload):
    url = "https://api.carbonintensity.org.uk/intensity"

    responses.add(
        responses.GET,
        url,
        json= valid_payload,
        status=200
    )

    data = get_carbon_intensity()

    assert data["from"] == datetime(2026, 11, 4, 16, 30, tzinfo=UTC)
    assert data["to"] == datetime(2026, 11, 4, 17, 0, tzinfo=UTC)
    assert data["forecast"] == 194
    assert data["actual"] == 198
    assert data["index"] == "high"


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


def test_save_carbon_intensity_to_json(tmp_path, valid_payload):

    filename = save_carbon_intensity_to_json(valid_payload, output_dir=tmp_path)

    assert filename.exists()

    with open(filename, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    print(loaded_data)
    assert loaded_data == valid_payload


def test_ingest_carbon_intensity(valid_payload):
    with patch(
            "main.fetch_carbon_intensity_raw",
            return_value=valid_payload) as mock_fetch, \
         patch(
            "main.upload_carbon_intensity_to_s3_bucket",
            return_value="s3://mock-bucket/carbon-intensity/2024-06-01_00-00-00-000000.json") as mock_upload:
        
        result = ingest_carbon_intensity()
        assert result == "s3://mock-bucket/carbon-intensity/2024-06-01_00-00-00-000000.json"
        mock_fetch.assert_called_once()
        mock_upload.assert_called_once_with(valid_payload)


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


def test_ingest_carbon_intensity_rejects_invalid_payload(valid_payload):
    del valid_payload["data"][0]["intensity"]["index"]

    with patch(
        "main.fetch_carbon_intensity_raw",
        return_value=valid_payload
    ) as mock_fetch, patch(
            "main.upload_carbon_intensity_to_s3_bucket",
            return_value="s3://mock-bucket/test.json"
    )as mock_upload:

        with pytest.raises(ValidationError):
            ingest_carbon_intensity()

        mock_fetch.assert_called_once()
        mock_upload.assert_not_called()


def test_ingest_carbon_intensity_preserves_unknown_fields(valid_payload):
    valid_payload["data"][0]["unknown_field"] = "unknown"

    with patch(
        "main.fetch_carbon_intensity_raw",
        return_value=valid_payload
    )as mock_fetch, patch(
        "main.upload_carbon_intensity_to_s3_bucket",
        return_value="s3://mock-bucket/test.json"
    )as mock_upload:

        ingest_carbon_intensity()

        uploaded_payload = mock_upload.call_args.args[0]
        mock_fetch.assert_called_once()
        assert uploaded_payload["data"][0]["unknown_field"] == "unknown"