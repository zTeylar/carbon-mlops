from datetime import UTC, datetime
import json
import os
from pathlib import Path
import logging
import requests
import boto3

from schemas import CarbonIntensityResponse


logger = logging.getLogger(__name__)


def fetch_carbon_intensity_raw() -> object:
    url = "https://api.carbonintensity.org.uk/intensity"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    raw_payload = response.json()
    logger.info("Fetched carbon intensity data from API.")
    return raw_payload


def get_carbon_intensity() -> dict[str]:
    raw_payload = fetch_carbon_intensity_raw()
    extracted_data = extract_carbon_intensity(raw_payload)
    return extracted_data


def extract_carbon_intensity(raw_payload):
    records = raw_payload.get("data")
    if not records:
        raise ValueError("Unexpected API response: 'data' missing or empty")
    record = records[0]
    from_ = datetime.fromisoformat(record["from"])
    to_ = datetime.fromisoformat(record["to"])
    forecast = record["intensity"]["forecast"]
    actual = record["intensity"]["actual"]
    index = record["intensity"]["index"]

    return {
        "from": from_,
        "to": to_,
        "forecast": forecast,
        "actual": actual,
        "index": index
    }


def save_carbon_intensity_to_json(data, output_dir=None) -> Path:
    if output_dir is None:
        dir_path = Path(__file__).parent / "data" / "raw"
    else:
        dir_path = Path(output_dir)
        
    dir_path.mkdir(parents=True, exist_ok=True)

    file_name = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    filename = dir_path / file_name

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
       
    return filename


def ingest_carbon_intensity() -> str:
    raw_payload = fetch_carbon_intensity_raw()
    CarbonIntensityResponse.model_validate(raw_payload)
    logger.info("Schema validation succeded")
    s3_uri = upload_carbon_intensity_to_s3_bucket(raw_payload)
    return s3_uri


def upload_carbon_intensity_to_s3_bucket(raw_payload, bucket_name=None, s3_client=None) -> str:
    if bucket_name is None:
        bucket_name = os.environ.get("CARBON_RAW_BUCKET")

    if not bucket_name:
        raise ValueError("CARBON_RAW_BUCKET environment variable is not set")
    
    if s3_client is None:
        s3_client = boto3.client("s3")

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S-%f")
    key = f"carbon-intensity/{timestamp}.json"
    body = json.dumps(raw_payload, indent=4).encode("utf-8")

    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=body,
        ContentType="application/json"
    )
    logger.info("Uploaded carbon intensity data to S3: s3://%s/%s", bucket_name, key)
    return f"s3://{bucket_name}/{key}"





def main() -> None:
    print(ingest_carbon_intensity())

if __name__ == "__main__":
    main()
