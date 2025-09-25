#!/usr/bin/env python3
"""
Test script for MCP tools functionality.
Tests tool calls through the MCP protocol.
"""

import requests
import json
import time
import subprocess
import sys

def establish_session(base_url="http://localhost:8000"):
    """Establish a session with the MCP server."""
    print("Establishing MCP session...")
    
    # Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=init_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        if response.status_code == 200:
            # Parse SSE response to get session info
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data:
                        print("✅ Session established successfully")
                        # Extract session ID from response headers
                        session_id = response.headers.get('mcp-session-id')
                        if session_id:
                            print(f"Session ID: {session_id}")
                        return session_id
        else:
            print(f"❌ Session establishment failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Session establishment error: {e}")
        return None

def test_tool_call(base_url="http://localhost:8000", tool_name="list_buckets", session_id=None):
    """Test calling a specific tool."""
    print(f"Testing tool call: {tool_name}")
    
    # Tool call request
    tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {}
        }
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Add session ID to headers if provided
    if session_id:
        headers["mcp-session-id"] = session_id
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=tool_request,
            headers=headers
        )
        
        if response.status_code == 200:
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data:
                        print(f"✅ Tool call successful")
                        print(f"Result: {json.dumps(data['result'], indent=2)}")
                        return True
                    elif 'error' in data:
                        print(f"❌ Tool call failed: {data['error']}")
                        return False
        else:
            print(f"❌ Tool call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Tool call error: {e}")
        return False

def test_csv_tool(base_url="http://localhost:8000", session_id=None):
    """Test CSV tool with sample data."""
    print("Testing CSV tool with sample data")
    
    # Tool call request for CSV summary
    tool_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "summarize_csv_file",
            "arguments": {
                "filename": "sample.csv"
            }
        }
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Add session ID to headers if provided
    if session_id:
        headers["mcp-session-id"] = session_id
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=tool_request,
            headers=headers
        )
        
        if response.status_code == 200:
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data:
                        print(f"✅ CSV tool call successful")
                        print(f"Result: {json.dumps(data['result'], indent=2)}")
                        return True
                    elif 'error' in data:
                        print(f"❌ CSV tool call failed: {data['error']}")
                        return False
        else:
            print(f"❌ CSV tool call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ CSV tool call error: {e}")
        return False

def start_server():
    """Start the MCP server in the background."""
    print("Starting MCP server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "simple_mcp_server.py"
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
    print("🧪 Testing MCP Tools")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("Failed to start server. Exiting.")
        sys.exit(1)
    
    try:
        # Establish session first
        session_id = establish_session()
        if not session_id:
            print("Failed to establish session. Exiting.")
            return
        
        print()
        
        # Test tool calls
        tests = [
            lambda: test_tool_call(tool_name="list_buckets", session_id=session_id),
            lambda: test_csv_tool(session_id=session_id)
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
            print("🎉 All tool tests passed! Your MCP server tools are working correctly.")
        else:
            print("⚠️  Some tool tests failed. Please check the output above.")
    
    finally:
        # Clean up server process
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
