"""The module contains class for interactive with VRChat API."""
import json
import logging
import os
import urllib
from pathlib import Path
from urllib.parse import urlencode

from requests import Response, Session
from requests.auth import HTTPBasicAuth
from requests.cookies import cookiejar_from_dict
from requests.utils import dict_from_cookiejar


class VRChatAPI:
    """Responsible for interacting with VRChat API"""

    BASE_URL = "https://vrchat.com/api/1"
    COOKIES_FILE_PATH = "cookies.json"

    def __init__(self) -> None:
        """Initialise new requests session and set common required headers."""
        self.session = Session()
        self.session.headers = {"User-Agent": "CustomPythonUserScript/0.0.1 (https://github.com/Gliger13)"}

    def basic_authentication(self, login: str, password: str) -> None:
        """Make basic authentication via login/password if needed.

        Load cookies from local storage.
        If none found send a request to login use with the given credentials.
        Save cookies in case of success.

        :param login: VRChat login.
        :param password: VRChat password.
        """
        if not login or not password:
            raise ValueError("Login and password were not provided. Unable to authenticate with the VRChat API")
        if not login:
            raise ValueError("Login was not provided. Unable to authenticate with the VRChat API")
        if not password:
            raise ValueError("Password was not provided. Unable to authenticate with the VRChat API")

        logging.debug("Checking if there are any cookies to load at %s", Path(self.COOKIES_FILE_PATH).absolute())
        self.load_cookies()
        if self.session.cookies:
            logging.debug("Cookies were found in the local storage. Using it")
            # TODO: Validate cookies
            return

        logging.info("Cookies were not found. Making login")
        login_response = self.login(login, password)
        if login_response.ok:
            self.save_cookies()
            logging.info("Login success. Cookies were saved")
        else:
            logging.error(f"Something went wrong during VRChat authentication. Response: {login_response.text}")
            login_response.raise_for_status()


    def mfa_authentication(self, mfa_code: str) -> None:
        logging.debug("Checking if Multi-factor Authentication is needed...")
        get_user_response = self.get_current_user()
        if mfa_methods := get_user_response.json().get("requiresTwoFactorAuth"):
            logging.info("Multi-factor Authentication is needed. Available options: %s", mfa_methods)
            if "totp" in mfa_methods:
                verify_response = self.verify_totp(mfa_code)
            elif "emailotp" in mfa_code:
                verify_response = self.verify_emailotp(mfa_code)
            else:
                raise NotImplementedError("Multi-factor Authentication methods %s are not supported", mfa_methods)
            if verify_response.ok:
                logging.info("MFA success. Saving cookies")
                self.save_cookies()
            else:
                logging.error(f"Something went wrong during VRChat MFA verify. Response: {verify_response.text}")
                verify_response.raise_for_status()

    def verify_totp(self, code: str) -> Response:
        response = self.session.post(url=f"{self.BASE_URL}/auth/twofactorauth/totp/verify", json={"code": code})
        return response

    def verify_emailotp(self, code: str) -> Response:
        response = self.session.post(url=f"{self.BASE_URL}/auth/twofactorauth/emailotp/verify", json={"code": code})
        return response

    def get_current_user(self) -> Response:
        response = self.session.get(f"{self.BASE_URL}/auth/user")
        return response

    def login(self, login: str, password: str) -> Response:
        login = os.getenv("LOGIN")
        password = os.getenv("PASSWORD")
        authentication = HTTPBasicAuth(urllib.parse.quote(login), urllib.parse.quote(password))
        response = self.session.get(url=f"{self.BASE_URL}/auth/user", auth=authentication)
        return response

    def switch_avatar(self, avatar_id: str) -> Response:
        response = self.session.put(f"{self.BASE_URL}/avatars/{avatar_id}/select")
        return response

    def get_avatars(self) -> Response:
        response = self.session.get(url=f"{self.BASE_URL}/avatars/favorites?featured=true")
        return response

    def save_cookies(self):
        cookies_jar = dict_from_cookiejar(self.session.cookies)
        Path("cookies.json").write_text(json.dumps(cookies_jar))

    def load_cookies(self):
        if os.path.exists(self.COOKIES_FILE_PATH):
            cookies = json.loads(Path(self.COOKIES_FILE_PATH).read_text())
            cookies_jar = cookiejar_from_dict(cookies)
            self.session.cookies = cookies_jar
