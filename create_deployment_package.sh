#!/bin/bash

# Script to create a deployment package for AWS Lambda following AWS documentation
set -e

echo "Creating AWS Lambda deployment package following AWS documentation..."

# Create package directory (following AWS docs)
PACKAGE_DIR="package"
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

# Generate requirements.txt from pyproject.toml
echo "Generating requirements.txt from pyproject.toml..."
uv export --format requirements-txt > requirements.txt

# Install dependencies in package directory
echo "Installing dependencies in package directory..."
# For x86_64 Lambda - use manylinux2014 platform for maximum compatibility
uv pip install --system --target ./package --python-platform x86_64-manylinux2014 --only-binary=:all: -r requirements.txt

# Alternative: For ARM64 Lambda (uncomment the line below and comment the line above)
# uv pip install --system --target ./package --python-platform aarch64-manylinux2014 --only-binary=:all: -r requirements.txt

# Runtime check for missing .so files
echo "Checking for native libraries..."
ls package/pydantic_core*/*.so || { echo "pydantic-core wheel missing!"; exit 1; }
echo "✅ pydantic-core native libraries found"

# Add source code files to package directory first
echo "Adding source code files to package directory..."
cp lambda_handler.py $PACKAGE_DIR/
cp fastapi_server.py $PACKAGE_DIR/
cp server.py $PACKAGE_DIR/
cp main.py $PACKAGE_DIR/
cp generate_parquet.py $PACKAGE_DIR/

# Add directories to package directory
cp -r tools/ $PACKAGE_DIR/
cp -r utils/ $PACKAGE_DIR/
cp -r prompts/ $PACKAGE_DIR/
cp -r resources/ $PACKAGE_DIR/
cp -r data/ $PACKAGE_DIR/

# Create zip file with everything at root (following AWS docs)
echo "Creating zip file with dependencies at root..."
cd $PACKAGE_DIR
zip -r ../mcp-server-deployment.zip .
cd ..

echo "Deployment package created: mcp-server-deployment.zip"
echo "Package size: $(du -h mcp-server-deployment.zip | cut -f1)"

# Clean up
rm -rf $PACKAGE_DIR

echo "Done! Following AWS Lambda deployment package structure."
