#!/usr/bin/env python3
"""
FastAPI-based MCP server with Streamable HTTP transport for serverless deployment.
Inspired by: https://heeki.medium.com/building-an-mcp-server-as-an-api-developer-cfc162d06a83
"""

import logging
import sys
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Only use stderr in Lambda (read-only filesystem)
    ],
)

logger = logging.getLogger(__name__)

# Create FastMCP instance with stateless HTTP support
mcp = FastMCP("S3 CSV Analysis Server", stateless_http=True)

# Import tools to auto-register them
import tools  # This will register all tools from the tools module

# Create FastAPI app with proper lifespan management
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MCP session manager")
    yield
    # Shutdown
    logger.info("Shutting down MCP session manager")

app = FastAPI(
    title="S3 CSV Analysis MCP Server",
    description="MCP server for analyzing CSV files from S3 and local storage",
    version="1.0.0",
    lifespan=lifespan
)

# Mount the MCP streamable HTTP app
app.mount("/mcp", mcp.streamable_http_app())

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the server."""
    return {"status": "healthy", "service": "S3 CSV Analysis MCP Server"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "S3 CSV Analysis MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI MCP server with Streamable HTTP transport")
    uvicorn.run(app, host="0.0.0.0", port=8000)
