"""
FRIDAY Error Manager Module
This module handles error logging and recovery for FRIDAY.
"""

import logging
import os
import traceback
import datetime

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/friday_error.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('friday_error_manager')

def log_error(error, context=None):
    """
    Log an error to the error log
    
    Args:
        error (Exception): The error to log
        context (str, optional): Additional context for the error
        
    Returns:
        None
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = f"ERROR at {timestamp}: {str(error)}"
    
    if context:
        error_message += f" | Context: {context}"
    
    logger.error(error_message)
    logger.error(traceback.format_exc())
    
    return error_message

def get_friendly_error_message(error):
    """
    Generate a user-friendly error message
    
    Args:
        error (Exception): The error to generate a message for
        
    Returns:
        str: A user-friendly error message
    """
    # Log the error
    log_error(error)
    
    # Generic friendly message
    return "I'm sorry, I encountered an error while processing your request. Please try again." 