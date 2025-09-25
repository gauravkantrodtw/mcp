#!/usr/bin/env python3
"""
Simple MCP server with Streamable HTTP transport.
Based on the article: https://heeki.medium.com/building-an-mcp-server-as-an-api-developer-cfc162d06a83
"""

import logging
import sys
from mcp.server.fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler(sys.stderr),
    ],
)

logger = logging.getLogger(__name__)

# Import the shared MCP instance and tools
from server import mcp
import tools  # This will register all tools from the tools module

logger.info("MCP Server initialized with tools")

if __name__ == "__main__":
    logger.info("Starting MCP server with Streamable HTTP transport")
    mcp.run(transport='streamable-http')
