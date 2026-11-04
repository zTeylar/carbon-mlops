from datetime import UTC, datetime
import json
import os
from pathlib import Path

import requests
import boto3


def fetch_carbon_intensity_raw():
    url = "https://api.carbonintensity.org.uk/intensity"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data


def get_carbon_intensity():
    data = fetch_carbon_intensity_raw()
    extracted_data = extract_carbon_intensity(data)
    return extracted_data


def extract_carbon_intensity(data):
    records = data.get("data")
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


def save_carbon_intensity_to_json(data, output_dir=None):
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


def ingest_carbon_intensity():
    data = fetch_carbon_intensity_raw()
    #file_path = save_carbon_intensity_to_json(data)
    s3_URI =upload_carbon_intensity_to_s3_bucket(data)
    return s3_URI


def upload_carbon_intensity_to_s3_bucket(data, bucket_name=None, s3_client=None):
    if bucket_name is None:
        bucket_name = os.environ.get("CARBON_RAW_BUCKET")

    if not bucket_name:
        raise ValueError("CARBON_RAW_BUCKET environment variable is not set")
    
    if s3_client is None:
        s3_client = boto3.client("s3")

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S-%f")
    key = f"carbon-intensity/{timestamp}.json"
    body = json.dumps(data, indent=4).encode("utf-8")

    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=body,
        ContentType="application/json"
    )

    return f"s3://{bucket_name}/{key}"





def main():
    print(ingest_carbon_intensity())

if __name__ == "__main__":
    main()
