import json
import time
import requests
import urllib3
from playwright.sync_api import sync_playwright

# Suppress InsecureRequestWarning globally for this module when verify=False is used.
# NOTE: Best practice is to fix the server certificate or configure requests to use
# a valid CA bundle. Use this suppression only when you understand and accept
# the risk of ignoring TLS verification.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token_cache.json"
# APP_URL = "https://dev.taskly.lilly.com/"  # Your web app URL
APP_URL="https://qa.taskly.lilly.com/"

# Keys in localStorage
TOKEN_KEY = "token"           # The key for access_token
USERID_KEY = "userId"         # The key for userId
CONVERSATION_KEY = "conversationId"  # The key for conversationId

# API_BASE_URL = "https://3exg2qgqb3-vpce-069388414a9f87f40.execute-api.us-east-2.amazonaws.com/dev/v2/ask"
API_BASE_URL = "https://k77ornbz5e-vpce-058757a9c034d181c.execute-api.us-east-2.amazonaws.com/qa/v2/ask"

def fetch_from_localstorage():
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    user_data_dir = r"C:\Users\L118384\AppData\Local\Microsoft\Edge\User Data\Default"

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=edge_path,
            headless=True,
            ignore_https_errors=True,
        )
        page = browser.new_page()

        # 🔹 Replace this with the EXACT domain from DevTools:
        page.goto("https://dev.taskly.lilly.com")  

        # Print all available keys and values
        all_data = page.evaluate("Object.entries(localStorage)")
        print("=== Raw localStorage ===")
        for key, val in all_data:
            print(f"{key}: {val}")

        # Try to get specific items
        token = page.evaluate("localStorage.getItem('token')")
        user_id = page.evaluate("localStorage.getItem('userId')")
        conversation_id = page.evaluate("localStorage.getItem('conversationId')")
        print("\nToken:", token)
        print("UserId:", user_id,'-----------',conversation_id)

        browser.close()
        return token,user_id,conversation_id

def get_token():
    """Check cached token, otherwise fetch from browser."""
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        if time.time() < data["expires_at"]:
            # print("Using cached token.")
            return data
    except FileNotFoundError:
        pass

    print("Fetching new token from browser...")
    token, user_id, conversation_id = fetch_from_localstorage()
    if not token or not user_id:
        raise Exception("Token or userId not found in localStorage!")

    # Cache with expiry
    token_data = {
        "access_token": token,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "expires_at": time.time() + 3500  # ~1 hour minus buffer
    }

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

    print("✅ Token cached.")
    return token_data

def ask_api(question):
    try:
        """Call /ask API using dynamic values from localStorage."""
        token_data = get_token()
        token = token_data["access_token"]
        user_id = token_data["user_id"]
        conversation_id = token_data.get("conversation_id")  # Can be None if new

        params = {
            "userId": user_id,
            "status": "true",
            "message": question,
            "isAgenticApproach": "false"
        }
        if conversation_id:
            params["conversationId"] = conversation_id

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(API_BASE_URL, headers=headers, params=params, verify=False)
        print("status code -----> ",response.status_code)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error calling ask_api:", str(e))
        return {"error": str(e)}

if __name__ == "__main__":
    question = "How to create a binder with template?"
    result = ask_api(question)
    with open("result.json", "w") as f:
        json.dump(result, f)
    print("API Response:", result)
