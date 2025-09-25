#!/usr/bin/env python3
"""
Deployment script for AWS Lambda MCP server.
Creates a deployment package and uploads to AWS Lambda.
"""

import os
import sys
import zipfile
import subprocess
import boto3
import json
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for AWS Lambda."""
    print("Creating deployment package...")
    
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
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Python files
        for file_path in files_to_include:
            if os.path.isfile(file_path):
                zipf.write(file_path)
                print(f"Added file: {file_path}")
            elif os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_full_path = os.path.join(root, file)
                            zipf.write(file_full_path)
                            print(f"Added file: {file_full_path}")
        
        # Add dependencies from site-packages
        try:
            import site
            site_packages = site.getsitepackages()[0]
            
            # Add specific packages needed for Lambda
            packages_to_include = [
                'mcp',
                'fastapi',
                'mangum',
                'pydantic',
                'uvicorn',
                'starlette',
                'boto3',
                'botocore',
                'pandas',
                'numpy'
            ]
            
            for package in packages_to_include:
                package_path = os.path.join(site_packages, package)
                if os.path.exists(package_path):
                    for root, dirs, files in os.walk(package_path):
                        for file in files:
                            if file.endswith(('.py', '.so', '.pyd')):
                                file_full_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_full_path, site_packages)
                                zipf.write(file_full_path, arcname)
                                print(f"Added dependency: {arcname}")
        except Exception as e:
            print(f"Warning: Could not add site-packages: {e}")
    
    print(f"Deployment package created: {zip_path}")
    return zip_path

def deploy_to_lambda(zip_path, function_name="mcp-server", region="eu-central-1"):
    """Deploy the package to AWS Lambda."""
    print(f"Deploying to AWS Lambda function: {function_name}")
    
    try:
        # Initialize boto3 client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Read the zip file
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"Successfully deployed to Lambda function: {response['FunctionName']}")
        print(f"Function ARN: {response['FunctionArn']}")
        
        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Handler="lambda_handler.lambda_handler",
            Runtime="python3.11",
            Timeout=30,
            MemorySize=512,
            Environment={
                'Variables': {
                    'AWS_PROFILE': 'tw-daap',
                    'AWS_REGION': region,
                    'FASTMCP_LOG_LEVEL': 'ERROR'
                }
            }
        )
        
        print("Function configuration updated successfully")
        
    except Exception as e:
        print(f"Error deploying to Lambda: {e}")
        return False
    
    return True

def main():
    """Main deployment function."""
    print("Starting AWS Lambda deployment for MCP server...")
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    # Deploy to Lambda
    success = deploy_to_lambda(zip_path)
    
    if success:
        print("Deployment completed successfully!")
        print("Your MCP server is now available as a serverless function.")
    else:
        print("Deployment failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
