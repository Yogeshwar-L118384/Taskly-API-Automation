"""
Utility functions for testing framework
Reusable helper functions for all tests
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

def save_response_to_json(response: Dict[str, Any], filename: str = None) -> Path:
    """
    Save API response to JSON file
    
    Args:
        response: Response dictionary
        filename: Output filename (auto-generated if not provided)
    
    Returns:
        Path to saved file
    """
    output_dir = Path("api_responses")
    output_dir.mkdir(exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_{timestamp}.json"
    
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)
    
    print(f" Response saved to {filepath}")
    return filepath

def validate_response(response: Dict[str, Any], required_keys: List[str] = None) -> bool:
    """
    Validate API response has required fields
    
    Args:
        response: Response dictionary
        required_keys: List of keys that must be present
    
    Returns:
        True if valid, False otherwise
    """
    required_keys = required_keys or ["answer", "message"]
    
    if isinstance(response, dict) and "error" in response:
        return False
    
    for key in required_keys:
        if key not in response:
            print(f"  Missing required key: {key}")
            return False
    
    return True

def measure_performance(func, *args, **kwargs) -> tuple:
    """
    Measure function execution time
    
    Args:
        func: Function to measure
        *args: Arguments for function
        **kwargs: Keyword arguments for function
    
    Returns:
        Tuple of (result, duration_seconds)
    """
    start = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start
    
    print(f"  Execution time: {duration:.2f}s")
    return result, duration

def compare_responses(response1: Dict, response2: Dict, keys_to_compare: List[str] = None) -> Dict[str, Any]:
    """
    Compare two API responses
    
    Args:
        response1: First response
        response2: Second response
        keys_to_compare: Specific keys to compare
    
    Returns:
        Comparison result dictionary
    """
    if keys_to_compare is None:
        keys_to_compare = ["answer", "message"]
    
    differences = {}
    
    for key in keys_to_compare:
        val1 = response1.get(key)
        val2 = response2.get(key)
        
        if val1 != val2:
            differences[key] = {
                "response1": val1,
                "response2": val2
            }
    
    return {
        "identical": len(differences) == 0,
        "differences": differences
    }

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry function on failure
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries (seconds)
    
    Returns:
        Function result
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1} failed: {str(e)}")
                print(f"   Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f" Failed after {max_retries} attempts")
                raise

def format_duration(seconds: float) -> str:
    """Format seconds to readable format"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"

def log_test_result(test_name: str, status: str, duration: float, details: Dict = None):
    """
    Log test result to console
    
    Args:
        test_name: Name of test
        status: Test status (PASSED, FAILED, SKIPPED)
        duration: Test duration in seconds
        details: Additional details
    """
    status_icon = {"PASSED": "✓", "FAILED": "✗", "SKIPPED": "⊘"}.get(status, "?")
    duration_str = format_duration(duration)
    
    print(f"\n{status_icon} {test_name}")
    print(f"   Status: {status}")
    print(f"   Duration: {duration_str}")
    
    if details:
        for key, value in details.items():
            print(f"   {key}: {value}")

def create_test_data_file(test_data: List[Dict], filename: str = "test_data.json") -> Path:
    """
    Create test data file
    
    Args:
        test_data: List of test data dictionaries
        filename: Output filename
    
    Returns:
        Path to created file
    """
    output_dir = Path("test_data")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)
    
    print(f" Test data saved to {filepath}")
    return filepath

def load_test_data(filename: str = "test_data.json") -> List[Dict]:
    """
    Load test data from file
    
    Args:
        filename: Input filename
    
    Returns:
        List of test data dictionaries
    """
    filepath = Path("test_data") / filename
    
    if not filepath.exists():
        print(f"  Test data file not found: {filepath}")
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
