#!/usr/bin/env python3
"""
Test script to verify MCP server configuration.
"""

import os
import sys
import subprocess
import json

def test_environment():
    """Test environment variables."""
    print("=== Environment Test ===")
    print(f"AWS_PROFILE: {os.environ.get('AWS_PROFILE', 'Not set')}")
    print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'Not set')}")
    print(f"FASTMCP_LOG_LEVEL: {os.environ.get('FASTMCP_LOG_LEVEL', 'Not set')}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")

def test_server_startup():
    """Test server startup."""
    print("\n=== Server Startup Test ===")
    
    # Test the exact command from the MCP config
    cmd = [
        "uv",
        "--directory",
        "/Users/gauravkantrod/Desktop/1_Databricks_accelerator/workspace/spike_fast_mcp",
        "run",
        "main.py"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Test with a simple request
        test_request = {
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
        
        result = subprocess.run(
            cmd,
            input=json.dumps(test_request) + "\n",
            text=True,
            capture_output=True,
            timeout=10,
            env={
                **os.environ,
                "AWS_PROFILE": "tw-daap",
                "AWS_REGION": "eu-central-1",
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                response = json.loads(result.stdout.strip())
                if "result" in response:
                    print("✅ Server startup test successful")
                    return True
                else:
                    print(f"❌ Server startup test failed: {response}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Server startup test failed - invalid JSON: {e}")
                return False
        else:
            print("❌ Server startup test failed - no response")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Server startup test failed - timeout")
        return False
    except Exception as e:
        print(f"❌ Server startup test error: {e}")
        return False

def test_tools_registration():
    """Test tools registration."""
    print("\n=== Tools Registration Test ===")
    
    try:
        # Import the server and check tools
        sys.path.insert(0, "/Users/gauravkantrod/Desktop/1_Databricks_accelerator/workspace/spike_fast_mcp")
        from server import mcp
        import tools
        
        # Check if tools are registered
        import asyncio
        async def check_tools():
            tools_list = await mcp.list_tools()
            return tools_list
        
        tools_list = asyncio.run(check_tools())
        print(f"✅ Tools registration test successful: {len(tools_list)} tools found")
        for tool in tools_list:
            print(f"  - {tool.name}: {tool.description}")
        return True
        
    except Exception as e:
        print(f"❌ Tools registration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing MCP Server Configuration")
    print("=" * 50)
    
    # Test environment
    test_environment()
    
    # Test server startup
    startup_success = test_server_startup()
    
    # Test tools registration
    tools_success = test_tools_registration()
    
    print("\n" + "=" * 50)
    print(f"Results: Startup={startup_success}, Tools={tools_success}")
    
    if startup_success and tools_success:
        print("🎉 All tests passed! MCP server configuration is working.")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
