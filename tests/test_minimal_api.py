



"""
4 Essential Test Cases - Aligned with Generic Framework
1) HTTP Status Code 200
2) Response JSON Format Check
3) CSV Questions - Read & Proper Output
4) Response Time Check
"""

import pytest
import csv
from pathlib import Path
from teh_ai.base_api_client import APIClient
from teh_ai.config import TASKLY_QA


# ================= FIXTURES =================

@pytest.fixture(scope="session")
def api_client():
    """Initialize API client with QA config"""
    return APIClient(TASKLY_QA)


@pytest.fixture
def csv_questions():
    """Load questions from CSV file"""
    csv_path = Path(__file__).parent / "test_questions.csv"
    if not csv_path.exists():
        pytest.skip(" CSV file not found")

    with open(csv_path, encoding="latin1") as f:
        return [row[0] for row in csv.reader(f) if row]


# ================= COMMON ASSERTION =================

def assert_api_success(response):
    """
    Standard API success validation
    """
    assert isinstance(response, dict), " Response is not a dict"
    assert response["status_code"] == 200, \
        f" API returned status {response['status_code']}"
    assert isinstance(response["body"], dict), " Response body is not JSON"
    assert "answer" in response["body"] or "message" in response["body"], \
        f" Missing answer/message: {response['body']}"


# ================= TEST 1: HTTP STATUS =================

@pytest.mark.smoke
def test_1_http_status_code(api_client):
    """Verify API returns HTTP 200"""
    response = api_client.call_api("Health check")
    assert response["status_code"] == 200
    print("✅ Test 1 PASSED: HTTP 200")


# ================= TEST 2: JSON FORMAT =================

@pytest.mark.smoke
@pytest.mark.sanity
def test_2_response_json_format(api_client):
    """Verify API response JSON structure"""
    response = api_client.call_api("What is RIM?")
    assert_api_success(response)
    print("✅ Test 2 PASSED: Valid JSON format")


# ================= TEST 3: CSV QUESTIONS =================

@pytest.mark.regression
def test_3_csv_questions_proper_output(api_client, csv_questions):
    """Verify API responses for all CSV questions"""
    for question in csv_questions:
        response = api_client.call_api(question)
        assert_api_success(response)

    print(f"✅ Test 3 PASSED: {len(csv_questions)} CSV questions validated")


# ================= TEST 4: RESPONSE TIME =================

@pytest.mark.smoke
# @pytest.mark.regression
def test_4_response_time_check(api_client):
    """Verify API response time is within limit"""
    response = api_client.call_api("What is TEH?")
    assert_api_success(response)

    assert response["response_time"] < 30, \
        f" Response took {response['response_time']:.2f}s (limit: 30s)"

    print(f"✅ Test 4 PASSED: Response time {response['response_time']:.2f}s")
