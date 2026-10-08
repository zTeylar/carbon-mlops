from datetime import datetime
import requests


def get_carbon_intensity():
    url = "https://api.carbonintensity.org.uk/intensity"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
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


def main():
    get_carbon_intensity()

if __name__ == "__main__":
    main()
