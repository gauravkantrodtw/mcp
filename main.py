#!/usr/bin/env python3
"""
Local entrypoint for running the MCP server directly.
"""

import logging
import sys
from server import mcp
import tools  # auto-registers CSV, Parquet, and S3 tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Only use stderr in Lambda (read-only filesystem)
    ],
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting MCP Server: S3 CSV Analysis Server")
    try:
        mcp.run()  # runs FastMCP in blocking mode
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()
