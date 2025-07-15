"""Initialize the CloudFormation documentation knowledge base."""

import logging
import threading
from awslabs.cfn_mcp_server.documentation_knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)

def initialize_knowledge_base():
    """Initialize the knowledge base in a background thread."""
    logger.info("Starting knowledge base initialization")
    
    def init_thread():
        try:
            # Get the knowledge base instance (this will load the documentation)
            kb = get_knowledge_base()
            doc_count = len(kb.document_index) if hasattr(kb, 'document_index') else 0
            logger.info(f"Knowledge base initialized with {doc_count} documents")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            # Don't let exceptions in initialization crash the server
            pass
    
    try:
        # Start initialization in a background thread
        thread = threading.Thread(target=init_thread)
        thread.daemon = True
        thread.start()
        return thread
    except Exception as e:
        logger.error(f"Failed to start knowledge base initialization thread: {e}")
        # Return None if thread creation fails
        return None