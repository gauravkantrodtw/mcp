# AWS Lambda Deployment Guide

This guide explains how to deploy the MCP Server to AWS Lambda using GitHub Actions.

## Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository with the code
3. AWS CLI configured (for local testing)

## Setup

### 1. AWS Credentials

Create an IAM user with the following permissions:
- `AWSLambdaFullAccess`
- `IAMFullAccess` (for creating the Lambda execution role)
- `AmazonS3ReadOnlyAccess` (for data access)

### 2. GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_SESSION_TOKEN`: Your AWS session token (optional, for temporary credentials like SSO/STS)

### 3. Deploy

The deployment happens automatically when you push to the `main` branch, or you can trigger it manually from the Actions tab.

## Manual Deployment (Local)

If you want to deploy manually from your local machine:

```bash
# 1. Create deployment package
./create_deployment_package.sh

# 2. Deploy to AWS
aws lambda create-function \
  --function-name mcp-server \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/mcp-server-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://mcp-server-deployment.zip \
  --architecture arm64 \
  --memory-size 512 \
  --timeout 30
```

## Testing

After deployment, you can test the function:

```bash
# Test the health endpoint
aws lambda invoke \
  --function-name mcp-server \
  --payload '{"httpMethod": "GET", "path": "/health"}' \
  response.json

cat response.json
```

## Configuration

You can modify the deployment settings in `.github/workflows/deploy.yml`:

- `AWS_REGION`: AWS region for deployment
- `FUNCTION_NAME`: Name of the Lambda function
- Memory size, timeout, and other Lambda settings

## Troubleshooting

1. **Permission errors**: Ensure your AWS credentials have the required permissions
2. **Role creation fails**: The role might already exist, this is normal
3. **Function not found**: Check the function name and region
4. **Package too large**: Lambda has a 50MB limit for direct uploads

## Monitoring

- View logs in AWS CloudWatch: `/aws/lambda/mcp-server`
- Monitor function metrics in the AWS Lambda console
- Set up CloudWatch alarms for errors and duration
