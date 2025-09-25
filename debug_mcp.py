#!/usr/bin/env python3
"""
Debug script to test MCP protocol communication.
"""

import json
import subprocess
import sys

def test_mcp_communication():
    """Test MCP communication with the server."""
    
    # Test 1: Initialize
    print("=== Test 1: Initialize ===")
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
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=json.dumps(init_request) + "\n",
            text=True,
            capture_output=True,
            timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0 and result.stdout.strip():
            response = json.loads(result.stdout.strip())
            if "result" in response:
                print("✅ Initialize successful")
                return True
            else:
                print(f"❌ Initialize failed: {response}")
                return False
        else:
            print("❌ Initialize failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Initialize error: {e}")
        return False

def test_tools_list():
    """Test tools/list after initialization."""
    print("\n=== Test 2: Tools List ===")
    
    # First initialize
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
    
    # Then list tools
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        # Send both requests
        input_data = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"
        
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2:  # tools/list response
                            if "result" in response:
                                tools = response["result"].get("tools", [])
                                print(f"✅ Tools list successful: {len(tools)} tools found")
                                for tool in tools:
                                    print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                                return True
                            else:
                                print(f"❌ Tools list failed: {response}")
                                return False
                    except json.JSONDecodeError:
                        continue
        else:
            print("❌ Tools list failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Debugging MCP Communication")
    print("=" * 50)
    
    # Test initialization
    init_success = test_mcp_communication()
    
    if init_success:
        # Test tools list
        tools_success = test_tools_list()
        
        print("\n" + "=" * 50)
        print(f"Results: Initialize={init_success}, Tools List={tools_success}")
        
        if init_success and tools_success:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed")
    else:
        print("❌ Initialization failed, skipping tools test")

if __name__ == "__main__":
    main()
