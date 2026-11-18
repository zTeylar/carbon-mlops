from main import ingest_carbon_intensity


def lambda_handler(event, context):
    try:
        s3_URI = ingest_carbon_intensity()

        if not s3_URI:
            raise RuntimeError("Failed to ingest carbon intensity data.")
        return {
            's3_URI': s3_URI,
            'body': 'Carbon intensity ingestion completed successfully.'
        }
    except Exception as e:
        print(f"Carbon intensity ingestion failed: {e}")
        raise
