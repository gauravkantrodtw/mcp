#!/bin/bash

# Script to destroy AWS resources created for the MCP Server
# This script will remove Lambda function, API Gateway, IAM roles, and permissions

set -e

# Configuration - modify these if you used different names
FUNCTION_NAME="mcp-server"
ROLE_NAME="mcp-server-role"
API_NAME="mcp-server-api"
AWS_REGION="eu-central-1"  # Change this to match your deployment region

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured and working"
}

# Function to get AWS account ID
get_account_id() {
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    if [ -z "$ACCOUNT_ID" ]; then
        print_error "Could not get AWS account ID"
        exit 1
    fi
    print_status "AWS Account ID: $ACCOUNT_ID"
}

# Function to confirm deletion
confirm_deletion() {
    echo
    print_warning "This script will destroy the following AWS resources:"
    echo "  - Lambda function: $FUNCTION_NAME"
    echo "  - API Gateway: $API_NAME"
    echo "  - IAM role: $ROLE_NAME"
    echo "  - Lambda permissions for API Gateway"
    echo "  - CloudWatch logs for the Lambda function"
    echo
    print_warning "This action cannot be undone!"
    echo
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Deletion cancelled by user"
        exit 0
    fi
}

# Function to remove Lambda permissions
remove_lambda_permissions() {
    print_status "Removing Lambda permissions for API Gateway..."
    
    # Get all permissions for the function
    PERMISSIONS=$(aws lambda get-policy --function-name "$FUNCTION_NAME" --query 'Policy' --output text 2>/dev/null || echo "")
    
    if [ -n "$PERMISSIONS" ]; then
        # Extract statement IDs for API Gateway permissions
        STATEMENT_IDS=$(echo "$PERMISSIONS" | jq -r '.Statement[] | select(.Principal.Service == "apigateway.amazonaws.com") | .Sid' 2>/dev/null || echo "")
        
        if [ -n "$STATEMENT_IDS" ]; then
            while IFS= read -r statement_id; do
                if [ -n "$statement_id" ] && [ "$statement_id" != "null" ]; then
                    print_status "Removing permission: $statement_id"
                    aws lambda remove-permission \
                        --function-name "$FUNCTION_NAME" \
                        --statement-id "$statement_id" 2>/dev/null || print_warning "Could not remove permission: $statement_id"
                fi
            done <<< "$STATEMENT_IDS"
        fi
    else
        print_status "No Lambda permissions found to remove"
    fi
}

# Function to delete API Gateway
delete_api_gateway() {
    print_status "Deleting API Gateway..."
    
    # Find API Gateway by name
    API_ID=$(aws apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text 2>/dev/null || echo "")
    
    if [ -n "$API_ID" ] && [ "$API_ID" != "None" ]; then
        print_status "Found API Gateway with ID: $API_ID"
        
        # Delete the API Gateway
        aws apigateway delete-rest-api --rest-api-id "$API_ID" 2>/dev/null || {
            print_warning "Could not delete API Gateway $API_ID, it may already be deleted or in use"
        }
        print_success "API Gateway deleted"
    else
        print_status "No API Gateway found with name: $API_NAME"
    fi
}

# Function to delete Lambda function
delete_lambda_function() {
    print_status "Deleting Lambda function..."
    
    # Check if function exists
    if aws lambda get-function --function-name "$FUNCTION_NAME" &>/dev/null; then
        print_status "Found Lambda function: $FUNCTION_NAME"
        
        # Delete the function
        aws lambda delete-function --function-name "$FUNCTION_NAME" 2>/dev/null || {
            print_error "Could not delete Lambda function: $FUNCTION_NAME"
            return 1
        }
        print_success "Lambda function deleted"
    else
        print_status "No Lambda function found with name: $FUNCTION_NAME"
    fi
}

# Function to delete CloudWatch logs
delete_cloudwatch_logs() {
    print_status "Deleting CloudWatch logs..."
    
    LOG_GROUP_NAME="/aws/lambda/$FUNCTION_NAME"
    
    # Check if log group exists
    if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP_NAME" --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "$LOG_GROUP_NAME"; then
        print_status "Found CloudWatch log group: $LOG_GROUP_NAME"
        
        # Delete the log group
        aws logs delete-log-group --log-group-name "$LOG_GROUP_NAME" 2>/dev/null || {
            print_warning "Could not delete CloudWatch log group: $LOG_GROUP_NAME"
        }
        print_success "CloudWatch logs deleted"
    else
        print_status "No CloudWatch log group found: $LOG_GROUP_NAME"
    fi
}

# Function to delete IAM role
delete_iam_role() {
    print_status "Deleting IAM role..."
    
    # Check if role exists
    if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
        print_status "Found IAM role: $ROLE_NAME"
        
        # Detach policies first
        print_status "Detaching policies from role..."
        
        # Detach AWS managed policies
        aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" 2>/dev/null || true
        aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" 2>/dev/null || true
        
        # Delete the role
        aws iam delete-role --role-name "$ROLE_NAME" 2>/dev/null || {
            print_error "Could not delete IAM role: $ROLE_NAME"
            print_warning "You may need to manually delete this role from the AWS Console"
            return 1
        }
        print_success "IAM role deleted"
    else
        print_status "No IAM role found with name: $ROLE_NAME"
    fi
}

# Function to clean up local files
cleanup_local_files() {
    print_status "Cleaning up local deployment files..."
    
    # Remove deployment package
    if [ -f "mcp-server-deployment.zip" ]; then
        rm -f mcp-server-deployment.zip
        print_success "Removed deployment package"
    fi
    
    # Remove test files
    if [ -f "test-payload.json" ]; then
        rm -f test-payload.json
        print_success "Removed test payload file"
    fi
    
    if [ -f "response.json" ]; then
        rm -f response.json
        print_success "Removed response file"
    fi
    
    # Remove package directory if it exists
    if [ -d "package" ]; then
        rm -rf package
        print_success "Removed package directory"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS MCP Server Resource Destruction Script"
    echo "=========================================="
    echo
    
    # Check prerequisites
    check_aws_cli
    get_account_id
    
    # Confirm deletion
    confirm_deletion
    
    echo
    print_status "Starting resource destruction..."
    echo
    
    # Remove resources in the correct order (dependencies first)
    remove_lambda_permissions
    delete_api_gateway
    delete_lambda_function
    delete_cloudwatch_logs
    delete_iam_role
    cleanup_local_files
    
    echo
    print_success "Resource destruction completed!"
    echo
    print_status "Summary of deleted resources:"
    echo "  ✓ Lambda function: $FUNCTION_NAME"
    echo "  ✓ API Gateway: $API_NAME"
    echo "  ✓ IAM role: $ROLE_NAME"
    echo "  ✓ Lambda permissions"
    echo "  ✓ CloudWatch logs"
    echo "  ✓ Local deployment files"
    echo
    print_status "All AWS resources have been successfully removed."
}

# Run main function
main "$@"
