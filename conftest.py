import pytest


@pytest.fixture(name="valid_payload")
def valid_payload_fixture():
    return {
        "data": [
            {
                "from": "2026-11-04T16:30Z",
                "to": "2026-11-04T17:00Z",
                "intensity": {
                    "forecast": 194,
                    "actual": 198,
                    "index": "high"
                }
            }
        ]
    }