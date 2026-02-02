"""
Example: Generic API Testing Framework
Shows how to use the framework with different APIs and parameters
"""
import pytest
from teh_ai.base_api_client import APIClient
from teh_ai.config import TASKLY_DEV, TASKLY_QA
from teh_ai.utils import (
    validate_response, 
    measure_performance, 
    compare_responses,
    save_response_to_json,
    log_test_result
)
import time

# =============================================================================
# Example 1: Testing Taskly DEV with default parameters
# =============================================================================

@pytest.fixture
def taskly_dev_client():
    """Create Taskly DEV client"""
    return APIClient(TASKLY_DEV)

def test_taskly_dev_basic(taskly_dev_client):
    """Test Taskly DEV API with basic parameters"""
    question = "What is RIM?"
    response = taskly_dev_client.call_api(question)
    
    assert validate_response(response), "Response validation failed"
    assert response.get("answer") or response.get("message"), "No answer in response"
    print(f"✓ Response: {response.get('answer', response.get('message'))[:100]}...")

# =============================================================================
# Example 2: Testing with custom parameters
# =============================================================================

def test_with_custom_params(taskly_dev_client):
    """Test API with custom parameters"""
    question = "How to create a binder?"
    
    # Override default parameters
    custom_params = {
        "userId": "custom_user_123",
        "status": "false"
    }
    
    response = taskly_dev_client.call_api(question, custom_params=custom_params)
    assert validate_response(response), "Response validation failed"

# =============================================================================
# Example 3: Performance testing
# =============================================================================

def test_api_performance(taskly_dev_client):
    """Test API response time"""
    question = "What is TEH?"
    
    # Measure performance
    response, duration = measure_performance(
        taskly_dev_client.call_api,
        question
    )
    
    assert duration < 30, f"API took {duration}s, expected < 30s"
    assert validate_response(response), "Response validation failed"
    
    log_test_result("API Performance Test", "PASSED", duration, 
                   {"question": question, "response_time": f"{duration:.2f}s"})

# =============================================================================
# Example 4: Comparing responses from different APIs
# =============================================================================

@pytest.fixture
def taskly_qa_client():
    """Create Taskly QA client"""
    return APIClient(TASKLY_QA)

def test_compare_dev_vs_qa(taskly_dev_client, taskly_qa_client):
    """Compare responses from DEV and QA environments"""
    question = "What is RIM?"
    
    response_dev = taskly_dev_client.call_api(question)
    response_qa = taskly_qa_client.call_api(question)
    
    # Compare responses
    comparison = compare_responses(response_dev, response_qa)
    
    print(f"\nDEV Response: {response_dev.get('answer', '')[:50]}...")
    print(f"QA Response: {response_qa.get('answer', '')[:50]}...")
    print(f"Identical: {comparison['identical']}")
    
    if comparison['differences']:
        print(f"Differences: {comparison['differences']}")

# =============================================================================
# Example 5: Batch testing with multiple questions
# =============================================================================

@pytest.mark.parametrize("question", [
    "What is RIM?",
    "How to create a binder with template?",
    "What is a binder template?",
    "How to use TEH AI?",
    "What are the features?"
])
def test_batch_questions(taskly_dev_client, question):
    """Test API with multiple questions"""
    start = time.time()
    response = taskly_dev_client.call_api(question)
    duration = time.time() - start
    
    # Validate response
    assert validate_response(response), f"Failed for question: {question}"
    
    # Log result
    log_test_result(f"Question: {question[:30]}", "PASSED", duration)
    
    # Save response
    save_response_to_json(response, f"response_{question[:20]}.json")

# =============================================================================
# Example 6: Testing with POST request
# =============================================================================

def test_post_request(taskly_dev_client):
    """Test API with POST request and custom data"""
    question = "What is RIM?"
    
    custom_data = {
        "priority": "high",
        "session_id": "session_123",
        "timeout": 30
    }
    
    response = taskly_dev_client.call_api_post(question, custom_data=custom_data)
    assert validate_response(response), "Response validation failed"

# =============================================================================
# Example 7: Error handling and retry logic
# =============================================================================

def test_error_handling(taskly_dev_client):
    """Test error handling"""
    # Test with None input
    response = taskly_dev_client.call_api(None)
    
    # Should contain error or be handled gracefully
    print(f"Error response: {response}")

# =============================================================================
# Usage Instructions:
# =============================================================================
"""
To run these examples:

1. Run all tests:
   pytest tests/test_generic_framework.py -v

2. Run specific test:
   pytest tests/test_generic_framework.py::test_taskly_dev_basic -v

3. Run with specific API (by changing fixture):
   pytest tests/test_generic_framework.py -v -k "test_taskly_dev"

4. Add your own test by:
   - Create new API config in config.py
   - Use APIClient(your_config) in fixture
   - Write test using the client

5. To add a new API:
   1. Add configuration in config.py:
      YOUR_API = {
          "api_base_url": "...",
          "params": {...},
          "headers": {...}
      }
   2. Create fixture:
      @pytest.fixture
      def your_api_client():
          return APIClient(YOUR_API)
   3. Write tests using the fixture
"""
