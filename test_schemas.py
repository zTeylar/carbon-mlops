import pytest
from pydantic import ValidationError
from schemas import CarbonIntensityResponse
from datetime import datetime, UTC


def test_valid_payload(valid_payload):
    validated_payload = CarbonIntensityResponse.model_validate(valid_payload)

    assert validated_payload.data[0].from_ == datetime(2026, 11, 4, 16, 30, tzinfo=UTC)
    assert validated_payload.data[0].to == datetime(2026, 11, 4, 17, 0, tzinfo=UTC)
    assert validated_payload.data[0].intensity.forecast == 194
    assert validated_payload.data[0].intensity.actual == 198
    assert validated_payload.data[0].intensity.index == "high"


def test_negative_forecast_is_rejected(valid_payload):
    valid_payload["data"][0]["intensity"]["forecast"] = -1

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_invalid_forecast_type(valid_payload):
    valid_payload["data"][0]["intensity"]["forecast"] = "194"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_invalid_actual_type(valid_payload):
    valid_payload["data"][0]["intensity"]["actual"] = "198"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_null_actual_is_accepted(valid_payload):
    valid_payload["data"][0]["intensity"]["actual"] = None
    validated_payload = CarbonIntensityResponse.model_validate(valid_payload)

    assert validated_payload.data[0].intensity.actual is None


def test_missing_actual_is_rejected(valid_payload):
    del valid_payload["data"][0]["intensity"]["actual"]

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_missing_data_is_rejected(valid_payload):
    del valid_payload["data"]

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_empty_data_list_is_rejected(valid_payload):
    valid_payload["data"] = []

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_missing_intensity_is_rejected(valid_payload):
    del valid_payload["data"][0]["intensity"]

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_missing_intensity_index_is_rejected(valid_payload):
    del valid_payload["data"][0]["intensity"]["index"]

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_invalid_intensity_index_is_rejected(valid_payload):
    valid_payload["data"][0]["intensity"]["index"] = "invalid"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_numeric_timestamp_is_rejected(valid_payload):
    valid_payload["data"][0]["from"] = 1234567890

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_malformed_timestamp_is_rejected(valid_payload):
    valid_payload["data"][0]["from"] = "not-a-timestamp"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_timezone_naive_timestamp_is_rejected(valid_payload):
    valid_payload["data"][0]["from"] = "2026-11-04T16:30"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_reversed_time_range_is_rejected(valid_payload):
    valid_payload["data"][0]["from"] = "2026-11-04T17:00Z"
    valid_payload["data"][0]["to"] = "2026-11-04T16:30Z"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_equal_timestamps_are_rejected(valid_payload):
    valid_payload["data"][0]["from"] = "2026-11-04T16:30Z"
    valid_payload["data"][0]["to"] = "2026-11-04T16:30Z"

    with pytest.raises(ValidationError):
        CarbonIntensityResponse.model_validate(valid_payload)


def test_unknown_fields_are_accepted(valid_payload):
    valid_payload["data"][0]["unexpected_field"] = "unexpected"
    validated_payload = CarbonIntensityResponse.model_validate(valid_payload)

    assert not hasattr(validated_payload.data[0], "unexpected_field")
