import logging
from server import mcp
from utils.file_reader import read_csv_from_s3, list_all_the_buckets


logger = logging.getLogger(__name__)

@mcp.tool()
def read_csv_file_data_s3(filepath: str) -> str:
    """
    Read CSV data directly from S3.
    Args:
        filepath: S3 path to the CSV file (e.g., 's3://bucket/path/file.csv')
    Returns:
        A string describing the file's contents.
    """
    logger.info(f"Reading CSV from S3: {filepath}")
    try:
        result = read_csv_from_s3(filepath)
        logger.info(f"Successfully read CSV from S3: {filepath}")
        return result
    except Exception as e:
        logger.error(f"Error reading CSV from S3 {filepath}: {e}")
        raise

@mcp.tool()
def list_buckets() -> str:
    """
    List all the buckets in the AWS S3.
    Returns:
        A string listing all available S3 buckets.
    """
    logger.info("Listing S3 buckets")
    try:
        result = list_all_the_buckets()
        logger.info("Successfully listed S3 buckets")
        return result
    except Exception as e:
        logger.error(f"Error listing S3 buckets: {e}")
        raise

