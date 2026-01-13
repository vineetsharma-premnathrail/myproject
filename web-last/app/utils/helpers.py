
# =========================================
# Helper Utilities
# =========================================
# Common utility functions used across the application for string cleaning,
# email validation, file size formatting, dictionary merging, and pagination.
#
# Usage:
#   from app.utils.helpers import ...

import re
from typing import Any, Dict, List

def clean_string(text: str) -> str:
    """
    Clean and normalize string input by removing extra whitespace.
    Args:
        text (str): Input string
    Returns:
        str: Cleaned string
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def validate_email(email: str) -> bool:
    """
    Validate if a string is a valid email address format.
    Args:
        email (str): Email address to validate
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_file_size(size_bytes: float) -> str:
    """
    Convert a file size in bytes to a human-readable string.
    Args:
        size_bytes (int): File size in bytes
    Returns:
        str: Formatted file size (e.g., '1.23 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary, returning a default if the key is missing.
    Args:
        data (dict): Dictionary to search
        key (str): Key to look up
        default (Any): Value to return if key is not found
    Returns:
        Any: Value from dict or default
    """
    return data.get(key, default)

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.
    Args:
        dict1 (dict): Base dictionary
        dict2 (dict): Dictionary to merge in
    Returns:
        dict: Merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def paginate_list(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    Paginate a list of items.
    Args:
        items (list): List of items to paginate
        page (int): Page number (1-based)
        per_page (int): Items per page
    Returns:
        dict: Pagination result with items, page info, and totals
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }