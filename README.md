# TEH_AI — Test Framework

This repository contains pytest tests for the TEH_AI API and scripts to generate an Allure HTML report.

## Prerequisites ✅
- Python 3.8+ and a virtual environment (we use `.\.venv`)
- Install Python dependencies in the venv (example):

```powershell
& .\.venv\Scripts\python.exe -m pip install pytest allure-pytest requests pandas openpyxl playwright
# then install Playwright browser binaries (if required):
& .\.venv\Scripts\python.exe -m playwright install
```

Notes:
- `allure` (classic CLI) requires Java on PATH. We include a local Allure CLI under `./tools/allure/*` for convenience.
- Alternatively, use `allurectl` (standalone binary) which does not require Java.

---

## Run tests (Allure results are created automatically)

pytest is configured in `pytest.ini` to write results to `allure-results/` and to clean the folder before each run.

PowerShell (recommended):

```powershell
# activate venv (if not already)
& .\.venv\Scripts\Activate.ps1

# run all tests (Allure results written automatically)
pytest -v

# run a specific test file
pytest tests/test_api.py -v

# run a single test function
pytest tests/test_api.py::test_token_retrieval -q

# run tests that load questions from CSV (the test iterates rows in tests/test_questions.csv)
pytest -k test_ask_api_with_questions_from_csv -v
```

---

## Generate and view the Allure report

Option A — Using local Allure CLI (bundled under `./tools` — requires Java in PATH):

```powershell
# generate static HTML report
& .\tools\allure\allure-2.35.1\bin\allure.bat generate allure-results -o allure-report --clean

# open served report (blocks terminal and prints URL)
& .\tools\allure\allure-2.35.1\bin\allure.bat serve allure-results

# or open static index.html (non-blocking)
Start-Process (Resolve-Path .\allure-report\index.html)
```

Option B — Using `allurectl` (standalone binary, no Java required):

```powershell
# if you have `allurectl` on PATH
allurectl generate -i allure-results -o allure-report
allurectl serve -i allure-results

# or run the generate+open sequence
allurectl generate -i allure-results -o allure-report; Start-Process (Resolve-Path .\allure-report\index.html)
```

If `allure` is not recognized: either call the tool with the full path (as above) or add the appropriate `bin` folder to your PATH.

---

## Test artifacts and logs

- `allure-results/` — raw results produced by pytest (fixtures and attachments are added by `tests/conftest.py`).
- `allure-report/` — generated static HTML report.
- `test_response_*.json` — per-question raw API responses produced by tests (attached to Allure and cleaned up by the cleanup fixture).
- `test_results/api_responses_<timestamp>.xlsx` — response summary Excel file produced when tests call `teh_ai.response_logger.ResponseLogger`.

---

## Troubleshooting

- Playwright browser downloads may fail under corporate TLS/proxies. Fixes:
	- Set `NODE_EXTRA_CA_CERTS` to a PEM file with your corporate CA.
	- Set `HTTP_PROXY`/`HTTPS_PROXY` environment variables.
	- Or download browsers on a machine with external access and copy them into the environment.
- If you get `allure` not recognized, use the local path `.\tools\allure\...` or install and add it to PATH.

---

If you'd like, I can add a convenience script `scripts/run_all.ps1` that runs pytest, generates the Allure report, and opens it automatically. Want me to add that?


<!-- -m pytest -v -->
<!-- generate allure-results -o allure-report --clean -->
<!-- serve allure-results -->

 <!-- .\.venv\Scripts\python.exe -m pytest -v -s
 .\tools\allure\allure-2.35.1\bin\allure.bat generate allure-results -o allure-report --clean
 .\tools\allure\allure-2.35.1\bin\allure.bat serve allure-results -->