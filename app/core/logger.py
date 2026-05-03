import logging
import json
import sys
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage()
        }
        
        # Add extra fields if passed via 'extra' dictionary
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
            
        return json.dumps(log_record)

def get_logger(name="rag"):
    logger = logging.getLogger(name)
    
    # Only configure if no handlers are present to prevent duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        
        # File handler
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setFormatter(JSONFormatter())
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger

log = get_logger()
