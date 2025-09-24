import logging
from server import mcp
from utils.file_reader import read_parquet_summary


logger = logging.getLogger(__name__)

@mcp.tool()
def summarize_parquet_file(filename: str) -> str:
    """
    Summarize a Parquet file by reporting its number of rows and columns.
    Args:
        filename: Name of the Parquet file in the /data directory (e.g., 'sample.parquet')
    Returns:
        A string describing the file's dimensions.
    """
    logger.info(f"Summarizing Parquet file: {filename}")
    try:
        result = read_parquet_summary(filename)
        logger.info(f"Successfully summarized Parquet file: {filename}")
        return result
    except Exception as e:
        logger.error(f"Error summarizing Parquet file {filename}: {e}")
        raise