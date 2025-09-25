#!/usr/bin/env python3
"""
Deployment script for AWS Lambda MCP server with dependencies.
Creates a deployment package with all required dependencies using uv.
"""

import os
import sys
import zipfile
import subprocess
import shutil
from pathlib import Path

def create_deployment_package_with_deps():
    """Create a deployment package for AWS Lambda with all dependencies."""
    print("📦 Creating deployment package with dependencies...")
    
    # Create a temporary directory for the deployment package
    temp_dir = "lambda_deployment_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Copy source files
        files_to_copy = [
            "lambda_handler.py",
            "fastapi_server.py", 
            "server.py",
            "tools/",
            "utils/",
            "resources/",
            "prompts/"
        ]
        
        for item in files_to_copy:
            if os.path.isfile(item):
                shutil.copy2(item, temp_dir)
                print(f"✅ Copied file: {item}")
            elif os.path.isdir(item):
                dest_dir = os.path.join(temp_dir, item)
                shutil.copytree(item, dest_dir)
                print(f"✅ Copied directory: {item}")
        
        # Install dependencies using uv
        print("📦 Installing dependencies with uv...")
        result = subprocess.run([
            "uv", "pip", "install", 
            "--target", temp_dir,
            "fastapi",
            "uvicorn[standard]",
            "mangum",
            "mcp",
            "boto3",
            "pandas",
            "pyarrow",
            "requests"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return None
        
        print("✅ Dependencies installed successfully")
        
        # Create zip file
        zip_path = "mcp-server-lambda-deployment.zip"
        
        # Remove existing zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"📦 Deployment package created: {zip_path}")
        print(f"📏 Package size: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")
        
        return zip_path
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("🧹 Cleaned up temporary directory")

def check_aws_credentials():
    """Check if AWS credentials are available."""
    print("🔐 Checking AWS credentials...")
    
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", "tw-daap"],
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
            "--region", region,
            "--profile", "tw-daap"
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
                "--environment", "Variables={AWS_PROFILE=tw-daap,FASTMCP_LOG_LEVEL=ERROR}",
                "--region", region,
                "--profile", "tw-daap"
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

def main():
    """Main deployment function."""
    print("🚀 AWS Lambda MCP Server Deployment (with dependencies)")
    print("=" * 60)
    
    # Create deployment package with dependencies
    zip_path = create_deployment_package_with_deps()
    
    if not zip_path:
        print("❌ Failed to create deployment package")
        return
    
    # Check AWS credentials
    if check_aws_credentials():
        # Deploy to Lambda
        success = deploy_to_lambda(zip_path)
        
        if success:
            print("\n🎉 Deployment completed successfully!")
            print("Your MCP server is now available as a serverless function.")
            print("\n📋 Test your deployment:")
            print("curl -X POST https://gvfbpeewz3.execute-api.eu-central-1.amazonaws.com/prod/mcp \\")
            print("    -H 'Content-Type: application/json' \\")
            print("    -H 'Accept: application/json, text/event-stream' \\")
            print("    -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"initialize\", \"params\": {\"protocolVersion\": \"2024-11-05\", \"capabilities\": {\"roots\": {\"listChanged\": true}, \"sampling\": {}}, \"clientInfo\": {\"name\": \"test-client\", \"version\": \"1.0.0\"}}}'")
        else:
            print("\n⚠️ Deployment failed.")
    else:
        print("\n⚠️ AWS credentials are not available.")
        print("Please refresh your credentials and try again.")

if __name__ == "__main__":
    main()
