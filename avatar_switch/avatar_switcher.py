"""Module with the class for switching to specific avatars."""

import logging
from typing import Mapping
from urllib.error import HTTPError

from requests import codes
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_fixed

from avatar_switch.errors import AuthenticationRequiredError
from avatar_switch.errors import AvatarNotFoundError
from avatar_switch.vrchat_api import VRChatAPI

logger = logging.getLogger("vrchat-avatar-switch")


class AvatarSwitcher:
    """Class that is responsible for switching to avatars.

    Pick avatars to switch from the given maps.
    Send requests to VRChat API to select the avatar.
    Handle possible VRChat API responses.
    """

    def __init__(self, api: VRChatAPI) -> None:
        """Initialize with the provided VRChatAPI with initialized request session."""
        self.api = api

    retry(
        retry=retry_if_exception_type(HTTPError),
        stop=stop_after_attempt(10),
        wait=wait_fixed(2),
        reraise=True,
    )

    def switch_avatar_by_name(self, avatars_map: Mapping[str, str], target_avatar_name: str) -> None:
        """Switch to the avatar that contains target avatar name using id from provided map.

        :param avatars_map: Dict/Map, where key - avatar id, value - avatar name.
        :param target_avatar_name: Target avatar name that should partially match the avatar name from the map.
        """
        if target_avatar_name is None:
            raise AvatarNotFoundError(f"Empty target avatar name was specified")
        for avatar_id, avatar_name in avatars_map.items():
            if target_avatar_name.lower() in avatar_name.lower():
                switch_avatar_response = self.api.switch_avatar(avatar_id)
                if switch_avatar_response.ok:
                    logger.info(f"Avatar was switched to `{avatar_name}`. Got: `{target_avatar_name}`")
                    return None
                elif switch_avatar_response.status_code in (codes.not_found, codes.forbidden):
                    logger.error(f"No avatar was found with id: {avatar_id}, name: {avatar_name}")
                    return None
                elif switch_avatar_response.status_code == codes.bad_request:
                    logger.error(
                        f"Failed to switch to avatar {avatar_name} - {avatar_id}. The request returned a 401 status "
                        f"code. Reauthentication is needed."
                    )
                    raise AuthenticationRequiredError(
                        "Request to switch avatar returned a 401 status code, "
                        "meaning authentication cookies are expired or missing"
                    )
                else:
                    logger.error(
                        f"Unexpected status code {switch_avatar_response.status_code} received in the request to "
                        f"switch avatar to {avatar_name} - {avatar_id}."
                    )
                    switch_avatar_response.raise_for_status()
        raise AvatarNotFoundError(f"No avatar was found that contains: `{target_avatar_name}`")

    def get_all_favorite_avatars(self) -> dict[str, str]:
        """Return all favorite avatars in format: id: name"""
        avatars_response = self.api.get_avatars()
        avatar_id_name_map: dict[str, str] = {}
        if avatars_response.ok:
            for avatar in avatars_response.json():
                avatar_id_name_map[avatar["id"]] = avatar["name"]
        return avatar_id_name_map
