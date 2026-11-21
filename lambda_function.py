import logging
from main import ingest_carbon_intensity


logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    
    try:
        logger.info("Starting carbon intensity ingestion process.")
        s3_URI = ingest_carbon_intensity()

        if not s3_URI:
            raise RuntimeError("Failed to ingest carbon intensity data.")
        logger.info("Carbon intensity ingestion completed successfully.")
        return {
            's3_URI': s3_URI,
            'body': 'Carbon intensity ingestion completed successfully.'
        }
    except Exception as e:
        logger.exception("Carbon intensity ingestion failed: %s", e)
        raise
