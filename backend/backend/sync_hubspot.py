import os
import logging
from dotenv import load_dotenv

from backend.connectors.hubspot import HubSpotConnector
from backend.knowledgebase import add_documents_to_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Syncs HubSpot data to the knowledge base."""
    load_dotenv()

    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not access_token:
        logger.error("HUBSPOT_ACCESS_TOKEN not found in environment variables.")
        return

    try:
        # We specify only the object types that are available in your HubSpot account.
        connector = HubSpotConnector(object_types=["contacts", "companies", "deals"])
        connector.load_credentials({"hubspot_access_token": access_token})

        logger.info("Starting HubSpot data sync...")
        document_batches = connector.load_from_state()

        for batch in document_batches:
            if batch:
                add_documents_to_knowledge_base(batch)
                logger.info(f"Added a batch of {len(batch)} documents to the knowledge base.")

        logger.info("HubSpot data sync finished.")

    except Exception as e:
        logger.error(f"An error occurred during HubSpot data sync: {e}", exc_info=True)

if __name__ == "__main__":
    main()
