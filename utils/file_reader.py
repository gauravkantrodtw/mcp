import pandas as pd
from pathlib import Path
import logging
import os

import boto3

# Create S3 client - in Lambda, use default credentials (IAM role)
# In local development, you can set AWS_PROFILE environment variable
s3 = boto3.client("s3", region_name="eu-central-1")

# Set up logging
logger = logging.getLogger(__name__)

# Base directory where our data lives
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def read_csv_summary(filename: str) -> str:
    """
    Read a CSV file and return a simple summary.
    Args:
        filename: Name of the CSV file (e.g. 'sample.csv')
    Returns:
        A string describing the file's contents.
    """
    logger.debug(f"Reading CSV summary for: {filename}")
    file_path = DATA_DIR / filename
    df = pd.read_csv(file_path)
    logger.info(f"CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns")
    return f"CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns."


def read_parquet_summary(filename: str) -> str:
    """
    Read a Parquet file and return a simple summary.
    Args:
        filename: Name of the Parquet file (e.g. 'sample.parquet')
    Returns:
        A string describing the file's contents.
    """
    logger.debug(f"Reading Parquet summary for: {filename}")
    file_path = DATA_DIR / filename
    df = pd.read_parquet(file_path)
    logger.info(f"Parquet file '{filename}' has {len(df)} rows and {len(df.columns)} columns")
    return f"Parquet file '{filename}' has {len(df)} rows and {len(df.columns)} columns."


def read_csv_data(filename: str) -> str:
    """
    Read a CSV file and return a data.
    Args:
        filename: Name of the CSV file (e.g. 'sample.csv')
    Returns:
        A string describing the file's contents.
    """
    logger.debug(f"Reading CSV data for: {filename}")
    file_path = DATA_DIR / filename
    df = pd.read_csv(file_path)
    logger.info(f"CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns")
    return f"""
        CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns.
        Data points are: {df.head()}
        """


def read_csv_from_s3(path: str) -> str:
    """Read a CSV directly from an S3 path like s3://bucket/key.csv"""
    logger.info(f"Reading CSV from S3: {path}")
    
    try:
        # Read CSV directly from S3 using pandas (s3fs handles credentials automatically)
        df = pd.read_csv(path)
        logger.info(f"Successfully read CSV from S3: {path} ({len(df)} rows, {len(df.columns)} columns)")
        
        result = f"""
        CSV file '{path}' has {len(df)} rows and {len(df.columns)} columns.
        Data points are: {df.head()}
        """
        return result
        
    except Exception as e:
        logger.error(f"Failed to read CSV from S3 path '{path}': {str(e)}")
        return f"Error reading S3 file: {str(e)}"



def list_all_the_buckets() -> str:
    """List all S3 buckets in the account"""
    logger.info("Listing S3 buckets")
    
    try:
        resp = s3.list_buckets()
        buckets = [b["Name"] for b in resp["Buckets"]]
        logger.info(f"Successfully listed {len(buckets)} S3 buckets: {buckets}")
        
        return f"Found {len(buckets)} S3 buckets:\n" + "\n".join([f"- {bucket}" for bucket in buckets])
        
    except Exception as e:
        logger.error(f"Failed to list S3 buckets: {str(e)}")
        return f"Error listing S3 buckets: {str(e)}"