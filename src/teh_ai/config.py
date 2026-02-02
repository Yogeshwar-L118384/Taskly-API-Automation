"""
Configuration for different APIs
Easy to switch between APIs or add new ones
"""

# Taskly API Configuration (DEV)
TASKLY_DEV = {
    "name": "Taskly Dev",
    "app_url": "https://dev.taskly.lilly.com/",
    "api_base_url": "https://3exg2qgqb3-vpce-069388414a9f87f40.execute-api.us-east-2.amazonaws.com/dev/v2/ask",
    "token_key": "token",
    "user_id_key": "userId",
    "conversation_key": "conversationId",
    "headers": {"Authorization": "Bearer {token}"},
    "params": {
        "userId": "{user_id}",
        "status": "true",
        "message": "{message}",
        "isAgenticApproach": "false",
        "conversationId": "{conversation_id}"
    }
}

# Taskly API Configuration (QA)
TASKLY_QA = {
    "name": "Taskly QA",
    "app_url": "https://qa.taskly.lilly.com/",
    "api_base_url": "https://k77ornbz5e-vpce-058757a9c034d181c.execute-api.us-east-2.amazonaws.com/qa/v2/ask",
    "token_key": "token",
    "user_id_key": "userId",
    "conversation_key": "conversationId",
    "headers": {"Authorization": "Bearer {token}"},
    "params": {
        "userId": "{user_id}",
        "status": "true",
        "message": "{message}",
        "isAgenticApproach": "false",
        "conversationId": "{conversation_id}"
    }
}

# Example: Generic REST API Configuration
GENERIC_REST_API = {
    "name": "Generic REST API",
    "app_url": "https://api.example.com/",
    "api_base_url": "https://api.example.com/v1/endpoint",
    "token_key": "access_token",
    "user_id_key": "user_id",
    "headers": {"Authorization": "Bearer {token}", "Content-Type": "application/json"},
    "params": {
        "user_id": "{user_id}",
        "query": "{message}",
        "session_id": "{session_id}"
    }
}

# Default configuration
DEFAULT_CONFIG = TASKLY_DEV

# Token cache file location
TOKEN_FILE = "token_cache.json"

# Browser configuration
BROWSER_CONFIG = {
    "edge_path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "user_data_dir": r"C:\Users\L118384\AppData\Local\Microsoft\Edge\User Data\Default",
    "headless": False,
    "ignore_https_errors": True,
    "timeout": 30000  # milliseconds
}

# Test configuration
TEST_CONFIG = {
    "default_timeout": 30,  # seconds
    "retry_count": 3,
    "log_responses": True,
    "excel_output": "test_results"
}
