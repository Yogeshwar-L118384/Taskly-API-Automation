# Generic API Testing Framework

## Architecture Overview

```
src/teh_ai/
├── config.py              ← API Configurations (centralized)
├── base_api_client.py     ← Generic API Client class (reusable)
├── utils.py               ← Utility functions (helpers)
├── response_logger.py     ← Existing (keeps working)
└── playwrt2.py            ← Legacy (can be retired)

tests/
├── test_generic_framework.py  ← New generic tests
└── test_api_1.py              ← Existing tests
```

---

## **1. config.py** - API Configurations

**Purpose**: Centralized storage for all API configurations

**How it works**:
- Define different API endpoints
- Specify required parameters for each API
- Switch between APIs easily

**Example**:
```python
TASKLY_DEV = {
    "app_url": "https://dev.taskly.lilly.com/",
    "api_base_url": "https://...",
    "params": {
        "userId": "{user_id}",
        "message": "{message}",
        "status": "true"
    }
}

YOUR_API = {
    "app_url": "https://your-api.com/",
    "api_base_url": "https://api.your-api.com/endpoint",
    "params": {
        "user_id": "{user_id}",
        "query": "{message}",
        "session": "{session_id}"
    }
}
```

**To add a new API**:
1. Add config to `config.py`
2. Use in tests: `APIClient(YOUR_API)`

---

## **2. base_api_client.py** - Generic API Client

**Purpose**: Single reusable class that works with ANY API

**Key Methods**:

### `__init__(config, token_file)`
Initialize client with configuration
```python
client = APIClient(TASKLY_DEV)
```

### `call_api(message, custom_params=None, **kwargs)`
Call API with GET request
```python
response = client.call_api(
    "What is RIM?",
    custom_params={"status": "false"},
    user_id="custom_id"
)
```

### `call_api_post(message, custom_data=None)`
Call API with POST request
```python
response = client.call_api_post(
    "Question here",
    custom_data={"priority": "high"}
)
```

### `get_token()`
Get token from cache or browser
```python
token_data = client.get_token()
```

**Features**:
-  Auto token extraction from localStorage
-  JWT decoding for user_id extraction
-  Token caching with expiry
-  Flexible parameter templating
-  Support for custom headers
-  GET and POST request methods

---

## **3. utils.py** - Helper Functions

**Available utilities**:

```python
# Validate response has required fields
validate_response(response, required_keys=["answer"])

# Measure execution time
result, duration = measure_performance(function, *args)

# Compare two responses
comparison = compare_responses(response1, response2)

# Save response to file
filepath = save_response_to_json(response, "filename.json")

# Retry failed functions
result = retry_on_failure(function, max_retries=3)

# Format duration nicely
duration_str = format_duration(seconds)

# Log test results
log_test_result("test_name", "PASSED", duration, details)

# Load/save test data
test_data = load_test_data("test_data.json")
filepath = create_test_data_file(test_data)
```

---

## **Usage Examples**

### Example 1: Test Taskly DEV

```python
import pytest
from teh_ai.base_api_client import APIClient
from teh_ai.config import TASKLY_DEV

@pytest.fixture
def client():
    return APIClient(TASKLY_DEV)

def test_taskly(client):
    response = client.call_api("What is RIM?")
    assert response.get("answer") is not None
```

### Example 2: Test Different API

```python
from teh_ai.config import YOUR_API

@pytest.fixture
def your_api_client():
    return APIClient(YOUR_API)

def test_your_api(your_api_client):
    response = your_api_client.call_api("Your question")
    assert response.get("answer") is not None
```

### Example 3: Parameterized Tests

```python
@pytest.mark.parametrize("question", [
    "What is RIM?",
    "How to create?",
    "Tell me more"
])
def test_multiple_questions(client, question):
    response = client.call_api(question)
    assert response.get("answer") is not None
```

### Example 4: Custom Parameters

```python
def test_custom_params(client):
    # Override default parameters
    response = client.call_api(
        "Question",
        custom_params={
            "userId": "custom_123",
            "status": "false"
        }
    )
    assert response.get("answer") is not None
```

### Example 5: Performance Testing

```python
from teh_ai.utils import measure_performance

def test_performance(client):
    response, duration = measure_performance(
        client.call_api,
        "What is RIM?"
    )
    assert duration < 30, "API took too long"
```

---

## **Adding a New API**

### Step 1: Add Config in `config.py`

```python
NEW_API = {
    "name": "My New API",
    "app_url": "https://myapi.com/",
    "api_base_url": "https://api.myapi.com/v1/query",
    "token_key": "access_token",  # Where token is stored in localStorage
    "user_id_key": "user_id",     # Where user_id is stored
    "headers": {
        "Authorization": "Bearer {token}",
        "Content-Type": "application/json"
    },
    "params": {
        "user_id": "{user_id}",
        "query": "{message}",
        "session_id": "{session_id}"
    }
}
```

### Step 2: Create Test Fixture

```python
import pytest
from teh_ai.base_api_client import APIClient
from teh_ai.config import NEW_API

@pytest.fixture
def new_api_client():
    return APIClient(NEW_API, token_file="new_api_token.json")
```

### Step 3: Write Tests

```python
def test_new_api(new_api_client):
    response = new_api_client.call_api("Your question")
    assert response.get("answer") is not None
```

---

## **Advantages of This Architecture**

 **Reusable**: Works with any API without code changes
 **Flexible**: Easy to add custom parameters
 **Maintainable**: Config centralized, logic separate
 **Testable**: Multiple test examples provided
 **Extensible**: Add new APIs without modifying base code
 **Scalable**: Handle multiple APIs in single test suite

---

## **Migration from Old Code**

Old way (hardcoded):
```python
API_BASE_URL = "https://..."
TOKEN_FILE = "token_cache.json"
def ask_api(question):
    # hardcoded logic
```

New way (generic):
```python
config = TASKLY_DEV  # or any other config
client = APIClient(config)
response = client.call_api("question")
```

---

## **Running Tests**

```bash
# Run all generic tests
pytest tests/test_generic_framework.py -v

# Run specific test
pytest tests/test_generic_framework.py::test_taskly_dev_basic -v

# Run with specific API
pytest tests/test_generic_framework.py -k "taskly" -v

# Run with detailed output
pytest tests/test_generic_framework.py -v -s
```

---

## **Summary**

| Component | Purpose | Benefit |
|-----------|---------|---------|
| **config.py** | Store API configurations | Easy to add new APIs |
| **base_api_client.py** | Generic client logic | Works with any API |
| **utils.py** | Helper functions | DRY principle |
| **test files** | Test cases | Show usage examples |

This structure makes it **easy to test multiple APIs** without duplicating code! 🚀

run framework 

\.venv\Scripts\python.exe  -m pytest tests/test_api_1.py -v --alluredir=allure-results