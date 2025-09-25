#!/usr/bin/env python3
"""
Simple deployment script for AWS Lambda MCP server.
Creates a deployment package and provides instructions for manual deployment.
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for AWS Lambda."""
    print("📦 Creating deployment package...")
    
    # Files to include in the package
    files_to_include = [
        "lambda_handler.py",
        "fastapi_server.py", 
        "server.py",
        "tools/",
        "utils/",
        "resources/",
        "prompts/"
    ]
    
    # Create zip file
    zip_path = "mcp-server-lambda-deployment.zip"
    
    # Remove existing zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Python files
        for file_path in files_to_include:
            if os.path.isfile(file_path):
                zipf.write(file_path)
                print(f"✅ Added file: {file_path}")
            elif os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_full_path = os.path.join(root, file)
                            zipf.write(file_full_path)
                            print(f"✅ Added file: {file_full_path}")
    
    print(f"📦 Deployment package created: {zip_path}")
    print(f"📏 Package size: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")
    return zip_path

def check_aws_credentials():
    """Check if AWS credentials are available."""
    print("🔐 Checking AWS credentials...")
    
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ AWS credentials are valid")
            return True
        else:
            print("❌ AWS credentials are invalid or expired")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ AWS CLI timeout")
        return False
    except FileNotFoundError:
        print("❌ AWS CLI not found")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS credentials: {e}")
        return False

def deploy_to_lambda(zip_path, function_name="mcp-server", region="eu-central-1"):
    """Deploy the package to AWS Lambda."""
    print(f"🚀 Deploying to AWS Lambda function: {function_name}")
    
    try:
        # Update function code
        result = subprocess.run([
            "aws", "lambda", "update-function-code",
            "--function-name", function_name,
            "--zip-file", f"fileb://{zip_path}",
            "--region", region
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully deployed to Lambda function")
            
            # Update function configuration
            config_result = subprocess.run([
                "aws", "lambda", "update-function-configuration",
                "--function-name", function_name,
                "--handler", "lambda_handler.lambda_handler",
                "--runtime", "python3.11",
                "--timeout", "30",
                "--memory-size", "512",
                "--environment", "Variables={AWS_PROFILE=tw-daap,AWS_REGION=eu-central-1,FASTMCP_LOG_LEVEL=ERROR}",
                "--region", region
            ], capture_output=True, text=True)
            
            if config_result.returncode == 0:
                print("✅ Function configuration updated successfully")
                return True
            else:
                print(f"⚠️ Function code deployed but configuration update failed: {config_result.stderr}")
                return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error deploying to Lambda: {e}")
        return False

def print_manual_deployment_instructions(zip_path):
    """Print manual deployment instructions."""
    print("\n" + "="*60)
    print("📋 MANUAL DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    print()
    print("If automatic deployment fails, you can deploy manually:")
    print()
    print("1. Refresh your AWS credentials:")
    print("   aws sso login --profile tw-daap")
    print()
    print("2. Deploy to Lambda:")
    print(f"   aws lambda update-function-code \\")
    print(f"       --function-name mcp-server \\")
    print(f"       --zip-file fileb://{zip_path} \\")
    print(f"       --region eu-central-1")
    print()
    print("3. Update function configuration:")
    print("   aws lambda update-function-configuration \\")
    print("       --function-name mcp-server \\")
    print("       --handler lambda_handler.lambda_handler \\")
    print("       --runtime python3.11 \\")
    print("       --timeout 30 \\")
    print("       --memory-size 512 \\")
    print("       --environment Variables='{AWS_PROFILE=tw-daap,AWS_REGION=eu-central-1,FASTMCP_LOG_LEVEL=ERROR}' \\")
    print("       --region eu-central-1")
    print()
    print("4. Test your deployment:")
    print("   curl -X POST https://YOUR_API_ID.execute-api.eu-central-1.amazonaws.com/prod/mcp \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -H 'Accept: application/json, text/event-stream' \\")
    print("       -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"initialize\", \"params\": {\"protocolVersion\": \"2024-11-05\", \"capabilities\": {\"roots\": {\"listChanged\": true}, \"sampling\": {}}, \"clientInfo\": {\"name\": \"test-client\", \"version\": \"1.0.0\"}}}'")
    print()

def main():
    """Main deployment function."""
    print("🚀 AWS Lambda MCP Server Deployment")
    print("=" * 50)
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    # Check AWS credentials
    if check_aws_credentials():
        # Deploy to Lambda
        success = deploy_to_lambda(zip_path)
        
        if success:
            print("\n🎉 Deployment completed successfully!")
            print("Your MCP server is now available as a serverless function.")
        else:
            print("\n⚠️ Automatic deployment failed.")
            print_manual_deployment_instructions(zip_path)
    else:
        print("\n⚠️ AWS credentials are not available.")
        print("Please refresh your credentials and try again.")
        print_manual_deployment_instructions(zip_path)

if __name__ == "__main__":
    main()
