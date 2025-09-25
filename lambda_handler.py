#!/usr/bin/env python3
"""
AWS Lambda handler for the FastAPI MCP server.
Uses Mangum adapter to convert API Gateway events to FastAPI requests.
"""

import logging
import os
from mangum import Mangum
from fastapi_server import app

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create Mangum adapter for FastAPI
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    logger.info(f"Received event: {event}")
    
    try:
        # Process the request through Mangum
        response = handler(event, context)
        logger.info(f"Response generated successfully")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": {
                "error": "Internal server error",
                "message": str(e)
            }
        }