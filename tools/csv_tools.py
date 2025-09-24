import logging
from server import mcp
from utils.file_reader import read_csv_summary, read_csv_data


logger = logging.getLogger(__name__)

@mcp.tool()
def summarize_csv_file(filename: str) -> str:
    """
    Summarize a CSV file by reporting its number of rows and columns.
    Args:
        filename: Name of the CSV file in the /data directory (e.g., 'sample.csv')
    Returns:
        A string describing the file's dimensions.
    """
    logger.info(f"Summarizing CSV file: {filename}")
    try:
        result = read_csv_summary(filename)
        logger.info(f"Successfully summarized CSV file: {filename}")
        return result
    except Exception as e:
        logger.error(f"Error summarizing CSV file {filename}: {e}")
        raise

@mcp.tool()
def read_csv_file_data(filename: str) -> str:
    """
    Read data from CSV file.
    Args:
        filename: Name of the CSV file in the /data directory (e.g., 'sample.csv')
    Returns:
        A string describing the file's dimensions.
    """
    logger.info(f"Reading CSV file data: {filename}")
    try:
        result = read_csv_data(filename)
        logger.info(f"Successfully read CSV file data: {filename}")
        return result
    except Exception as e:
        logger.error(f"Error reading CSV file data {filename}: {e}")
        raise