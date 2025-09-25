#!/usr/bin/env python3
"""
Test script for the FastAPI MCP server.
Tests both local functionality and MCP protocol compliance.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

def test_health_endpoint(base_url="http://localhost:8000"):
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_root_endpoint(base_url="http://localhost:8000"):
    """Test the root endpoint."""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_mcp_initialize(base_url="http://localhost:8000"):
    """Test MCP initialization."""
    print("Testing MCP initialization...")
    try:
        # MCP initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp/",
            json=init_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP initialization successful")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ MCP initialization failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ MCP initialization error: {e}")
        return False

def test_mcp_tools_list(base_url="http://localhost:8000"):
    """Test MCP tools list."""
    print("Testing MCP tools list...")
    try:
        # MCP tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            f"{base_url}/mcp/",
            json=tools_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP tools list successful")
            print(f"Available tools: {len(result.get('result', {}).get('tools', []))}")
            for tool in result.get('result', {}).get('tools', []):
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return True
        else:
            print(f"❌ MCP tools list failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ MCP tools list error: {e}")
        return False

def start_server():
    """Start the FastAPI server in the background."""
    print("Starting FastAPI server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "fastapi_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def main():
    """Main test function."""
    print("🧪 Testing FastAPI MCP Server")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("Failed to start server. Exiting.")
        sys.exit(1)
    
    try:
        # Test endpoints
        tests = [
            test_health_endpoint,
            test_root_endpoint,
            test_mcp_initialize,
            test_mcp_tools_list
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        print("=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your FastAPI MCP server is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the output above.")
    
    finally:
        # Clean up server process
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
