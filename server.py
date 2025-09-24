import logging
from mcp.server.fastmcp import FastMCP

# Set up logger for server module
logger = logging.getLogger(__name__)

# This is the shared MCP server instance
mcp = FastMCP("S3 CSV Analysis Server")

# Log server initialization
logger.info("MCP Server instance created: S3 CSV Analysis Server")
