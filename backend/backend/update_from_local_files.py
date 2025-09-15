import logging
from backend.knowledgebase import update_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting knowledge base update from local files...")
    update_knowledge_base()
    logger.info("Knowledge base update from local files finished.")
