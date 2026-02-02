"""
Generic API Client for testing different APIs
Supports multiple API configurations and parameters
"""
import json
import time
import requests
import urllib3
from typing import Dict, Any
from playwright.sync_api import sync_playwright
from teh_ai.config import DEFAULT_CONFIG, BROWSER_CONFIG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIClient:
    """Generic API Client for making API calls and fetching authentication tokens from browser localStorage."""

    def __init__(self, config: Dict[str, Any] = None, token_file: str = "token_cache.json"):
        """
        Initializes the API client with configuration and token caching.

        Args:
            config (Dict[str, Any], optional): API and browser configuration.
            token_file (str): File path to cache token data.
        """
        self.config = config or DEFAULT_CONFIG
        self.token_file = token_file
        self.token_data = None
        self._load_cached_token()

    # ---------------- TOKEN HANDLING ----------------

    def _load_cached_token(self):
        """
        Loads token data from the cache file if it exists and is still valid.

        Returns:
            bool: True if a valid cached token was loaded, False otherwise.
        """
        try:
            with open(self.token_file) as f:
                data = json.load(f)
            if time.time() < data.get("expires_at", 0):
                self.token_data = data
                print(f"✅ Using cached token from {self.token_file}")
                return True
        except FileNotFoundError:
            pass
        return False

    def _save_token(self, token: str, user_id: str, extra_data: Dict = None):
        """
        Saves token data to the cache file along with expiration time.

        Args:
            token (str): Access token.
            user_id (str): User identifier.
            extra_data (Dict, optional): Additional token-related information.

        Returns:
            Dict: Token data saved to file.
        """
        token_data = {
            "access_token": token,
            "user_id": user_id,
            "expires_at": time.time() + 3500,
            **(extra_data or {})
        }
        with open(self.token_file, "w") as f:
            json.dump(token_data, f)

        self.token_data = token_data
        print(f"✅ Token cached to {self.token_file}")
        return token_data

    def fetch_token_from_browser(self) -> Dict[str, str]:
        """
        Launches a browser using Playwright to fetch token, user_id, and conversation_id
        from the application's localStorage.

        Returns:
            Dict[str, str]: Dictionary containing token, user_id, and conversation_id.
        """
        print(f"🔐 Fetching token from browser at {self.config['app_url']}")

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_CONFIG["user_data_dir"],
                executable_path=BROWSER_CONFIG["edge_path"],
                headless=BROWSER_CONFIG["headless"],
                ignore_https_errors=BROWSER_CONFIG["ignore_https_errors"],
            )
            page = browser.new_page()

            try:
                page.goto(
                    self.config["app_url"],
                    wait_until="networkidle",
                    timeout=BROWSER_CONFIG["timeout"]
                )
                time.sleep(2)

                token_key = self.config.get("token_key", "token")
                user_id_key = self.config.get("user_id_key", "userId")
                conversation_key = self.config.get("conversation_key", "conversationId")

                token = page.evaluate(f"localStorage.getItem('{token_key}')")
                user_id = page.evaluate(f"localStorage.getItem('{user_id_key}')")
                conversation_id = page.evaluate(f"localStorage.getItem('{conversation_key}')")

                if not token or not user_id:
                    raise RuntimeError("Token or user_id not found in localStorage")

                return {
                    "token": token,
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }
            finally:
                browser.close()

    def get_token(self) -> Dict[str, str]:
        """
        Returns the cached token if available; otherwise fetches a new token
        from the browser and saves it to the cache.

        Returns:
            Dict[str, str]: Token data including access_token, user_id, and conversation_id.
        """
        if self.token_data:
            return self.token_data

        result = self.fetch_token_from_browser()
        self._save_token(
            result["token"],
            result["user_id"],
            {"conversation_id": result.get("conversation_id")}
        )
        return self.token_data

    # ---------------- API CALL ----------------

    def call_api(self, message: str, custom_params: Dict = None, **kwargs) -> Dict[str, Any]:
        """
        Makes a GET API request using the configured headers and parameters.
        Automatically injects the access token and user details into the request.

        Args:
            message (str): Main message to send in API parameters.
            custom_params (Dict, optional): Additional parameters to include in the request.
            **kwargs: Other dynamic parameters for API request.

        Returns:
            Dict[str, Any]: Dictionary containing status_code, response_time, and response body.
        """
        token_data = self.get_token()
        token = token_data["access_token"]
        user_id = token_data["user_id"]

        # Build params
        params = {}
        for key, value in self.config.get("params", {}).items():
            if value.startswith("{"):
                name = value.strip("{}")
                if name == "message":
                    params[key] = message
                elif name == "user_id":
                    params[key] = user_id
                elif name == "conversation_id":
                    params[key] = token_data.get("conversation_id")
                elif name in kwargs:
                    params[key] = kwargs[name]
            else:
                params[key] = value

        if custom_params:
            params.update(custom_params)

        headers = {}
        for key, value in self.config.get("headers", {}).items():
            if value == "{token}":
                headers[key] = f"Bearer {token}"
            else:
                headers[key] = value

        api_url = self.config["api_base_url"]

        print(f"\n➡️ Calling API: {api_url}")
        print(f"   Params: {params}")

        start = time.time()
        response = requests.get(
            api_url,
            headers=headers,
            params=params,
            verify=False,
            timeout=30
        )
        duration = time.time() - start

        print(f"   Status: {response.status_code}")
        response.raise_for_status()

        return {
            "status_code": response.status_code,
            "response_time": duration,
            "body": response.json()
        }


# """
# Generic API Client for testing different APIs
# Supports multiple API configurations and parameters
# """
# import json
# import time
# import requests
# import urllib3
# import base64
# from typing import Dict, Any
# from playwright.sync_api import sync_playwright
# from teh_ai.config import DEFAULT_CONFIG, BROWSER_CONFIG

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# class APIClient:
#     """Generic API Client that works with any API (TEST FRIENDLY)"""

#     def __init__(self, config: Dict[str, Any] = None, token_file: str = "token_cache.json"):
#         self.config = config or DEFAULT_CONFIG
#         self.token_file = token_file
#         self.token_data = None
#         self._load_cached_token()

#     # ---------------- TOKEN HANDLING ----------------

#     def _load_cached_token(self):
#         try:
#             with open(self.token_file) as f:
#                 data = json.load(f)
#             if time.time() < data.get("expires_at", 0):
#                 self.token_data = data
#                 print(f"✅ Using cached token from {self.token_file}")
#                 return True
#         except FileNotFoundError:
#             pass
#         return False

#     def _save_token(self, token: str, user_id: str, extra_data: Dict = None):
#         token_data = {
#             "access_token": token,
#             "user_id": user_id,
#             "expires_at": time.time() + 3500,
#             **(extra_data or {})
#         }
#         with open(self.token_file, "w") as f:
#             json.dump(token_data, f)

#         self.token_data = token_data
#         print(f"✅ Token cached to {self.token_file}")
#         return token_data

#     def _extract_jwt_claims(self, token: str) -> Dict:
#         try:
#             parts = token.split('.')
#             if len(parts) >= 2:
#                 payload = parts[1]
#                 padding = 4 - len(payload) % 4
#                 if padding != 4:
#                     payload += '=' * padding
#                 decoded = base64.urlsafe_b64decode(payload)
#                 return json.loads(decoded)
#         except Exception as e:
#             print(f"⚠️ Could not decode JWT: {e}")
#         return {}

#     def fetch_token_from_browser(self) -> Dict[str, str]:
#         print(f"🔐 Fetching token from browser at {self.config['app_url']}")

#         with sync_playwright() as p:
#             browser = p.chromium.launch_persistent_context(
#                 user_data_dir=BROWSER_CONFIG["user_data_dir"],
#                 executable_path=BROWSER_CONFIG["edge_path"],
#                 headless=BROWSER_CONFIG["headless"],
#                 ignore_https_errors=BROWSER_CONFIG["ignore_https_errors"],
#             )
#             page = browser.new_page()

#             try:
#                 page.goto(
#                     self.config["app_url"],
#                     wait_until="networkidle",
#                     timeout=BROWSER_CONFIG["timeout"]
#                 )
#                 time.sleep(2)

#                 token_key = self.config.get("token_key", "token")
#                 user_id_key = self.config.get("user_id_key", "userId")
#                 conversation_key = self.config.get("conversation_key", "conversationId")

#                 token = page.evaluate(f"localStorage.getItem('{token_key}')")
#                 user_id = page.evaluate(f"localStorage.getItem('{user_id_key}')")
#                 conversation_id = page.evaluate(f"localStorage.getItem('{conversation_key}')")

#                 if not token:
#                     raise RuntimeError("Token not found in localStorage")

#                 if not user_id:
#                     claims = self._extract_jwt_claims(token)
#                     user_id = claims.get("uid") or claims.get("preferred_username")

#                 return {
#                     "token": token,
#                     "user_id": user_id,
#                     "conversation_id": conversation_id
#                 }
#             finally:
#                 browser.close()

#     def get_token(self) -> Dict[str, str]:
#         if self.token_data:
#             return self.token_data

#         result = self.fetch_token_from_browser()
#         self._save_token(
#             result["token"],
#             result["user_id"],
#             {"conversation_id": result.get("conversation_id")}
#         )
#         return self.token_data

#     # ---------------- API CALL ----------------

#     def call_api(self, message: str, custom_params: Dict = None, **kwargs) -> Dict[str, Any]:
#         """
#         Returns:
#         {
#             status_code: int,
#             response_time: float,
#             body: dict
#         }
#         """
#         token_data = self.get_token()
#         token = token_data["access_token"]
#         user_id = token_data["user_id"]

#         # Build params
#         params = {}
#         for key, value in self.config.get("params", {}).items():
#             if value.startswith("{"):
#                 name = value.strip("{}")
#                 if name == "message":
#                     params[key] = message
#                 elif name == "user_id":
#                     params[key] = user_id
#                 elif name == "conversation_id":
#                     params[key] = token_data.get("conversation_id")
#                 elif name in kwargs:
#                     params[key] = kwargs[name]
#             else:
#                 params[key] = value

#         if custom_params:
#             params.update(custom_params)

#         headers = {}
#         for key, value in self.config.get("headers", {}).items():
#             if value == "{token}":
#                 headers[key] = f"Bearer {token}"
#             else:
#                 headers[key] = value

#         api_url = self.config["api_base_url"]

#         print(f"\n➡️ Calling API: {api_url}")
#         print(f"   Params: {params}")

#         start = time.time()
#         response = requests.get(
#             api_url,
#             headers=headers,
#             params=params,
#             verify=False,
#             timeout=30
#         )
#         duration = time.time() - start

#         print(f"   Status: {response.status_code}")
#         response.raise_for_status()

#         return {
#             "status_code": response.status_code,
#             "response_time": duration,
#             "body": response.json()
#         }
