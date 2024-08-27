"""The module contains class for interactive with VRChat API."""

import json
import logging
import os
import urllib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from requests import Response
from requests import Session
from requests import codes
from requests.auth import HTTPBasicAuth
from requests.cookies import cookiejar_from_dict
from requests.utils import dict_from_cookiejar

logger = logging.getLogger("vrchat-avatar-switch")


class VRChatAPI:
    """Responsible for interacting with VRChat API."""

    BASE_URL = "https://vrchat.com/api/1"
    COOKIES_FILE_PATH = "cookies.json"

    def __init__(self) -> None:
        """Initialise new requests session and set common required headers."""
        self.session = Session()
        self.session.headers = {"User-Agent": "vrchat-avatar-switch/1.0.0 https://github.com/Gliger13/vrchat_avatar_switcher"}

    def authenticate(self, login: str, password: str, mfa_code: str | None = None) -> None:
        """Authenticate through all layers."""
        self.basic_authentication(login, password)
        self.mfa_authentication(mfa_code)

    def basic_authentication(self, login: str, password: str) -> None:
        """Make basic authentication via login/password if needed.

        Load cookies from local storage.
        If none found send a request to login use with the given credentials.
        Save cookies in case of success.

        :param login: VRChat login.
        :param password: VRChat password.
        """
        logger.info("Checking if there are any cookies to load at %s", Path(self.COOKIES_FILE_PATH).absolute())
        self._load_cookies()
        if self.session.cookies:
            logger.info("Cookies were found in the local storage. Validating them...")
            current_user_response = self.get_current_user()
            if current_user_response.ok:
                logger.info("Cookies are valid")
                return None
            else:
                logger.info("Cookies has expired. New login is required")

        if not login:
            input("Login: ")
        if not password:
            input("Password: ")

        if not login or not password:
            raise ValueError("Login and password were not provided. Unable to authenticate with the VRChat API")
        if not login:
            raise ValueError("Login was not provided. Unable to authenticate with the VRChat API")
        if not password:
            raise ValueError("Password was not provided. Unable to authenticate with the VRChat API")

        logger.info("Making login")
        login_response = self.login(login, password)
        if login_response.ok:
            self._save_cookies()
            logger.info(f"Login success. Cookies were saved")
            self.log_authentication_cookie_expiration_date()
        elif login_response.status_code == codes.forbidden:
            logger.error(
                f"Authentication failed. High-likely invalid credentials were provided. Response: {login_response.text}"
            )
            login_response.raise_for_status()
        else:
            logger.error(f"Something went wrong during VRChat authentication. Response: {login_response.text}")
            login_response.raise_for_status()
        return None

    def mfa_authentication(self, mfa_code: str | None = None) -> None:
        """Checks if MFA Authentication is needed and performs it.

        :param mfa_code: Optional MFA code. If empty console input will be asked.
        """
        logger.debug("Checking if Multi-factor Authentication is needed...")
        get_user_response = self.get_current_user()
        if mfa_methods := get_user_response.json().get("requiresTwoFactorAuth"):
            logger.info("Multi-factor Authentication is needed. Available options: %s", mfa_methods)
            while not mfa_code:
                method = "MFA Application" if "totp" in mfa_methods else "email code"
                mfa_code = input(
                    f"Multi-factor Authentication is needed to finish authentication using {method}. "
                    f"Please enter the code: "
                )
            if "totp" in mfa_methods:
                verify_response = self.verify_totp(mfa_code)
            elif "emailotp" in mfa_code:
                verify_response = self.verify_emailotp(mfa_code)
            else:
                raise NotImplementedError("Multi-factor Authentication methods %s are not supported", mfa_methods)

            if verify_response.ok:
                logger.info("MFA success. Saving cookies")
                self._save_cookies()
            elif verify_response.status_code == codes.bad_request:
                logger.error(f"Multi-factor Authentication has failed. Retrying...")
                self.mfa_authentication()
            else:
                logger.error(f"Something went wrong during VRChat MFA verify. Response: {verify_response.text}")
                verify_response.raise_for_status()
        else:
            logger.info("Multi-factor Authentication is not needed")

    def verify_totp(self, code: str) -> Response:
        """Send POST request to verify MFA TOTP code."""
        response = self.session.post(url=f"{self.BASE_URL}/auth/twofactorauth/totp/verify", json={"code": code})
        return response

    def verify_emailotp(self, code: str) -> Response:
        """Send POST request to verify MFA email code."""
        response = self.session.post(url=f"{self.BASE_URL}/auth/twofactorauth/emailotp/verify", json={"code": code})
        return response

    def get_current_user(self) -> Response:
        """Send GET request to get the current user."""
        response = self.session.get(f"{self.BASE_URL}/auth/user")
        return response

    def login(self, login: str, password: str) -> Response:
        """Send GET request with encoded login/password to get the authentication cookie."""
        authentication = HTTPBasicAuth(urllib.parse.quote(login), urllib.parse.quote(password))
        response = self.session.get(url=f"{self.BASE_URL}/auth/user", auth=authentication)
        return response

    def switch_avatar(self, avatar_id: str) -> Response:
        """Send a PUT request to switch to the given avatar by its ID."""
        response = self.session.put(f"{self.BASE_URL}/avatars/{avatar_id}/select")
        return response

    def get_avatars(self) -> Response:
        """Send GET avatar with the given query.

        :return: Response to request to get avatars using given query.
        """
        response = self.session.get(url=f"{self.BASE_URL}/avatars/favorites?featured=true")
        return response

    def _save_cookies(self) -> None:
        """Transform cookies from the current session into a cookie jar and save them locally."""
        cookies_jar = dict_from_cookiejar(self.session.cookies)
        Path(self.COOKIES_FILE_PATH).write_text(json.dumps(cookies_jar))

    def _load_cookies(self) -> None:
        """Load cookies from the file and set them in the current session."""
        if os.path.exists(self.COOKIES_FILE_PATH):
            cookies = json.loads(Path(self.COOKIES_FILE_PATH).read_text())
            cookies_jar = cookiejar_from_dict(cookies)
            self.session.cookies = cookies_jar

    def log_authentication_cookie_expiration_date(self) -> None:
        """Log the time when the authentication cookie will expire."""
        if authentication_cookie := [cookie for cookie in self.session.cookies if cookie.name == "auth"][0]:
            expiration_time = datetime.fromtimestamp(int(authentication_cookie.expires))
            logger.info(f"Authentication cookies expire at: {expiration_time}")
