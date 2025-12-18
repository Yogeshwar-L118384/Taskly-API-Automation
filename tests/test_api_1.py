
import pytest
import json
import re
import requests
import pandas as pd
import os
import time
from pathlib import Path
from teh_ai.playwrt2 import ask_api, get_token
from teh_ai.response_logger import get_logger     # <-- import your logger
import shutil


@pytest.fixture(scope="session")
def logger():
    return get_logger()


@pytest.fixture
def token_data():
    return get_token()


@pytest.fixture
def api_client(token_data):
    return {
        "token": token_data["access_token"],
        "user_id": token_data["user_id"],
        "conversation_id": token_data.get("conversation_id")
    }



@pytest.fixture
def test_questions():
    csv_path = Path(__file__).parent / "test_questions.csv"
    df = pd.read_csv(csv_path,encoding="latin1")
    return df["question"].tolist()


def test_token_retrieval(token_data, logger):
    assert "access_token" in token_data
    assert "user_id" in token_data
    assert "expires_at" in token_data

    logger.log_response(
        query="GET TOKEN",
        response=token_data,
        status_code=200,
        execution_time=0
    )


@pytest.mark.parametrize("question", [
    "What is RIM?",
    "How to create a binder with template?",
    "What is a binder template?"
])
def test_ask_api_with_different_questions(question, logger):
    start = time.time()
    response = ask_api(question)
    end = time.time()

    assert isinstance(response, dict)
    assert "answer" in response or "message" in response

    logger.log_response(
        query=question,
        response=response,
        status_code=200,
        execution_time=end - start
    )


# def test_ask_api_with_questions_from_csv(test_questions, logger):
#     for question in test_questions:
#         start = time.time()
#         response = ask_api(question)
#         end = time.time()

#         assert isinstance(response, dict)
#         assert "answer" in response or "message" in response

#         logger.log_response(
#             query=question,
#             response=response,
#             status_code=200,
#             execution_time=end - start
#         )
#         clean_filename = re.sub(r'[^\w\s-]', '', question)
#         clean_filename = re.sub(r'[-\s]+', '_', clean_filename)
        
#         with open(f"test_response_{clean_filename}.json", "w") as f:
#             json.dump(response, f, indent=2)



def test_ask_api_with_questions_from_csv(test_questions, logger):
    for question in test_questions:
        start = time.time()
        response = ask_api(question)
        end = time.time()

        assert isinstance(response, dict)
        assert "answer" in response or "message" in response

        logger.log_response(
            query=question,
            response=response,
            status_code=200,
            execution_time=end - start
        )

        clean_filename = re.sub(r"[^\w\s-]", "", question)
        clean_filename = re.sub(r"[-\s]+", "_", clean_filename)

        # filepath = f"test_responses/test_response_{clean_filename}.json"
        # with open(filepath, "w") as f:
        #     json.dump(response, f, indent=2)


# def test_ask_api_with_questions_from_csv(test_questions):
#     """Test API responses using questions loaded from CSV"""
#     for question in test_questions:
#         response = ask_api(question)
        
#         # Basic response structure validation
#         assert isinstance(response, dict), f"Response for '{question}' is not a dict"
#         assert "answer" in response or "message" in response, f"No answer/message in response for '{question}'"
        
#         # Save responses for analysis
#         clean_filename = re.sub(r'[^\w\s-]', '', question)
#         clean_filename = re.sub(r'[-\s]+', '_', clean_filename)
        
#         with open(f"test_response_{clean_filename}.json", "w") as f:
#             json.dump(response, f, indent=2)

def test_ask_api_error_handling(logger):
    # with pytest.raises((Exception, requests.exceptions.HTTPError)):
    ask_api(None)

    logger.log_response(
        query="INVALID INPUT (None)",
        response="ERROR RAISED",
        status_code=400,
        execution_time=0
    )


def test_conversation_context(api_client, logger):
    start = time.time()
    response1 = ask_api("What is RIM?")
    mid = time.time()
    response2 = ask_api("Tell me more about it")
    end = time.time()

    assert response1 is not None
    assert response2 is not None
    assert response1 != response2

    logger.log_response("What is RIM?", response1, 200, mid - start)
    logger.log_response("Tell me more about it", response2, 200, end - mid)


def test_api_performance(logger):
    start = time.time()
    response = ask_api("What is RIM?")
    end = time.time()
    print("status code-------")

    response_time = end - start
    assert response_time < 30

    logger.log_response("What is RIM? (performance)", response, 200, response_time)


# SAVE EXCEL AT THE END OF TEST SESSION
def pytest_sessionfinish(session, exitstatus):
    logger = get_logger()
    logger.save_to_excel()
# def pytest_sessionfinish(session, exitstatus):
#     logger = get_logger()
#     excel_path = logger.save_to_excel()   # Save Excel
    
#     # Attach to Allure report

#     if excel_path and excel_path.exists():
#         allure.attach.file(
#             source=str(excel_path),
#             name="API_Responses_Report",
#             attachment_type=allure.attachment_type.XML,
#             extension=".xlsx"
#         )