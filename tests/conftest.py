import logging
import pathlib
import glob
import allure
import pytest
from teh_ai.response_logger import get_logger     # <-- import your logger
import allure

@pytest.fixture(autouse=True)
def test_logger(request, tmp_path):
    """Create a per-test log file and attach it to the test node for later use.

    The fixture yields a logger instance. After the test finishes, the
    `pytest_runtest_makereport` hook will attach the log file to the Allure
    result.
    """
    # sanitize test name to form a safe filename on Windows
    import re
    test_name = request.node.name
    safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', test_name)
    log_file = tmp_path / f"{safe_name}.log"

    logger = logging.getLogger(test_name)
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Make log path available on the node
    request.node._test_log_path = str(log_file)

    try:
        yield logger
    finally:
        # remove handler to flush
        logger.removeHandler(handler)
        handler.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # Only attach for the call phase (when the test actually ran)
    if rep.when == "call":
        # Attach the per-test log file if present
        log_path = getattr(item, "_test_log_path", None)
        if log_path and pathlib.Path(log_path).exists():
            try:
                allure.attach.file(log_path, name="test-log", attachment_type=allure.attachment_type.TEXT)
            except Exception:
                pass

        # Attach captured stdout/stderr if available
        try:
            if hasattr(rep, "capstdout") and rep.capstdout:
                allure.attach(rep.capstdout, name="stdout", attachment_type=allure.attachment_type.TEXT)
            if hasattr(rep, "capstderr") and rep.capstderr:
                allure.attach(rep.capstderr, name="stderr", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass

        # Attach any test response JSON files created by tests
        for fname in glob.glob("test_response_*.json"):
            try:
                allure.attach.file(fname, name=pathlib.Path(fname).name, attachment_type=allure.attachment_type.JSON)
            except Exception:
                pass


# import allure


# def pytest_sessionfinish(session, exitstatus):
#     logger = get_logger()
#     excel_path = logger.save_to_excel()

#     if excel_path and excel_path.exists():
#         allure.attach.file(
#             source=str(excel_path),
#             name="API_Responses_Report",
#             attachment_type=allure.attachment_type.XML,
#             extension=".xlsx"
#         )

import pytest
import os
import shutil
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
# from response_logger import get_logger

import pytest
import os
import shutil
import uuid
import json
# from response_logger import get_logger


def pytest_sessionfinish(session, exitstatus):
    logger = get_logger()
    excel_path = logger.save_to_excel()

    print("\n pytest_sessionfinish CALLED")
    print("Collected responses:", len(logger.data))
    print("Excel Path:", excel_path)

    if not excel_path:
        return

    # Find the Allure results directory
    results_dir = (
        session.config.option.allure_report_dir 
        or session.config.option.allure_results_dir
    )

    if not results_dir:
        print(" Allure is not enabled. Run pytest with --alluredir=allure-results")
        return

    os.makedirs(results_dir, exist_ok=True)

    # Unique ID for the attachment
    attachment_uuid = str(uuid.uuid4())
    attachment_filename = f"{attachment_uuid}-attachment.xlsx"
    attachment_file_path = os.path.join(results_dir, attachment_filename)

    # Copy Excel file into allure-results
    shutil.copyfile(str(excel_path), attachment_file_path)

    # Create the JSON metadata for Allure
    attachment_json = {
        "name": "API Responses Excel Report",
        "source": attachment_filename,
        "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    # Save JSON into allure-results
    with open(os.path.join(results_dir, f"{attachment_uuid}-attachment.json"), "w") as f:
        json.dump(attachment_json, f)

    print("Excel attached to Allure successfully.")



# import pytest
# import os
# import shutil
# import json
# import re
# import uuid
# import time
# from pathlib import Path
# from teh_ai.response_logger import get_logger

# # Folder where all JSON outputs are stored
# JSON_DIR = Path("json_outputs")


# # ---------------------------------------------------------
# # SAFE WINDOWS DELETE
# # ---------------------------------------------------------
# def safe_rmtree(path: Path):
#     """Safely remove a folder even on Windows (handles PermissionError)."""
#     if not path.exists():
#         return

#     for _ in range(10):  # retry 10 times
#         try:
#             shutil.rmtree(path)
#             return
#         except PermissionError:
#             time.sleep(0.3)  # wait a bit, then retry

#     # Final fallback
#     shutil.rmtree(path, ignore_errors=True)


# # ---------------------------------------------------------
# # CLEANUP BEFORE TEST SESSION
# # ---------------------------------------------------------
# def pytest_sessionstart(session):
#     # Clean old JSON safely
#     safe_rmtree(JSON_DIR)
#     JSON_DIR.mkdir(parents=True, exist_ok=True)

#     # Clean old Excel logs
#     logger = get_logger()
#     logger.cleanup_old_excels()

#     print("Session start: Cleaned old JSON + Excel logs")


# # ---------------------------------------------------------
# # GLOBAL LOGGER FIXTURE
# # ---------------------------------------------------------
# @pytest.fixture(scope="session")
# def logger():
#     return get_logger()


# # ---------------------------------------------------------
# # DECORATOR: MEASURE API EXECUTION TIME
# # ---------------------------------------------------------
# def measure_time(func):
#     """Decorator for timing API calls only."""
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         exec_time = time.time() - start
#         return result, exec_time
#     return wrapper


# # Expose timed ask_api to tests
# # (Tests must import timed_ask_api from here)
# timed_api = None  # will be set dynamically in tests


# # ---------------------------------------------------------
# # SAVE JSON UTIL FOR TEST FILES
# # ---------------------------------------------------------
# def save_json(question: str, response: dict):
#     """Save JSON response into json_outputs folder with clean filename."""
#     filename = re.sub(r"[^\w\s-]", "", question)
#     filename = re.sub(r"[-\s]+", "_", filename)
#     filepath = JSON_DIR / f"{filename}.json"

#     with open(filepath, "w") as f:
#         json.dump(response, f, indent=2)

#     return filepath


# # ---------------------------------------------------------
# # ATTACH EXCEL TO ALLURE
# # ---------------------------------------------------------
# def pytest_sessionfinish(session, exitstatus):
#     logger = get_logger()
#     excel_path = logger.save_to_excel()

#     print("\npytest_sessionfinish Called")
#     print("Collected API responses:", len(logger.data))
#     print("Excel Path:", excel_path)

#     if not excel_path:
#         return

#     # Find Allure results directory
#     results_dir = (
#         session.config.option.allure_report_dir
#         or session.config.option.allure_results_dir
#     )

#     if not results_dir:
#         print("Allure is NOT enabled. Use: pytest --alluredir=allure-results")
#         return

#     os.makedirs(results_dir, exist_ok=True)

#     # Unique ID
#     attachment_uuid = str(uuid.uuid4())
#     attachment_filename = f"{attachment_uuid}-attachment.xlsx"
#     attachment_path = os.path.join(results_dir, attachment_filename)

#     shutil.copyfile(str(excel_path), attachment_path)

#     # Create JSON metadata for Allure
#     attachment_json = {
#         "name": "API Responses Excel Report",
#         "source": attachment_filename,
#         "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     }

#     with open(os.path.join(results_dir, f"{attachment_uuid}-attachment.json"), "w") as f:
#         json.dump(attachment_json, f)

#     print("Excel report successfully attached to Allure.")
