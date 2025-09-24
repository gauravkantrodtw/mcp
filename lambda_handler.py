#!/usr/bin/env python3
"""
AWS Lambda entrypoint for the MCP server.
"""

import logging
import time
import asyncio
import json
from mangum import Mangum
from server import mcp
import tools  # auto-registers all MCP tools

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global handler instance (created once per Lambda container)
_handler = None

async def handle_mcp_request(request_body: str) -> dict:
    """Handle MCP request directly without streamable HTTP manager"""
    try:
        # Parse the JSON-RPC request
        request_data = json.loads(request_body)
        
        # Handle different MCP methods
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id")
        
        if method == "tools/list":
            tools_list = await mcp.list_tools()
            result = [{"name": tool.name, "description": tool.description} for tool in tools_list]
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = await mcp.call_tool(tool_name, tool_args)
        else:
            result = {"error": f"Unknown method: {method}"}
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id") if 'request_data' in locals() else None,
            "error": {"code": -32603, "message": "Internal error"}
        }

def get_handler():
    """Get or create a custom handler that bypasses streamable HTTP manager"""
    global _handler
    if _handler is None:
        # Create a simple ASGI app that handles MCP requests
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        
        async def mcp_endpoint(request):
            body = await request.body()
            result = await handle_mcp_request(body.decode())
            return JSONResponse(result)
        
        async def health_endpoint(request):
            return JSONResponse({
                "status": "healthy",
                "service": "MCP Server",
                "timestamp": time.time()
            })
        
        app = Starlette(routes=[
            Route("/mcp", mcp_endpoint, methods=["POST"]),
            Route("/health", health_endpoint, methods=["GET"])
        ])
        _handler = Mangum(app, lifespan="off")
    return _handler

def lambda_handler(event, context):
    """Lambda handler function"""
    start_time = time.time()
    try:
        handler = get_handler()
        response = handler(event, context)
        logger.info("Processed request in %.3fs", time.time() - start_time)
        return response
    except Exception as e:
        logger.error("Lambda handler error: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "Internal server error"}'
        }

# Local test mode
if __name__ == "__main__":
    test_event = {
        "version": "2.0",
        "routeKey": "POST /mcp",
        "rawPath": "/mcp",
        "rawQueryString": "",
        "headers": {
            "content-type": "application/json",
            "host": "localhost"
        },
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/mcp",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-agent"
            },
            "requestId": "test-request-id",
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "stage": "test"
        },
        "body": '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}',
        "isBase64Encoded": False,
    }

    result = lambda_handler(test_event, None)
    print(result)
