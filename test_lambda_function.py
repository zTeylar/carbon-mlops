import pytest
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler


def test_lambda_handler_success():
    with patch('lambda_function.ingest_carbon_intensity', return_value="s3://bucket/key") as mock:
        result = lambda_handler(None, None)

        assert result['s3_URI'] == "s3://bucket/key"
        mock.assert_called_once()


def test_lambda_handler_failure():
    with patch('lambda_function.ingest_carbon_intensity', side_effect=RuntimeError("Ingestion failed")) as mock:
        with pytest.raises(RuntimeError, match="Ingestion failed"):
            lambda_handler(None, None)
        mock.assert_called_once()
