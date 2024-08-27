"""Basic script to switch avatars using the console."""

import logging.config
import os

from avatar_switch.avatar_switcher import AvatarSwitcher
from avatar_switch.errors import AuthenticationRequiredError
from avatar_switch.errors import AvatarNotFoundError
from avatar_switch.vrchat_api import VRChatAPI

logger = logging.getLogger("vrchat-avatar-switch")

AVATARS_MAP: dict[str, str] = {
    # "{vrchat_avatar_id}": "{any avatar name}"
    # "avtr_00000000-0000-0000-0000-000000000000": "My Avatar Name",
}


def console_switch() -> None:
    """Switch VRChat avatars using the console."""
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
    logger.info("VRChat avatar switcher console script")

    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    mfa_code = os.getenv("MFA_CODE")

    vrchat_api = VRChatAPI()
    vrchat_api.authenticate(login, password, mfa_code)
    avatar_switcher = AvatarSwitcher(vrchat_api)
    avatars_map = AVATARS_MAP or avatar_switcher.get_all_favorite_avatars()
    while True:
        avatar_name = input("Waiting for avatar name: ")
        try:
            avatar_switcher.switch_avatar_by_name(avatars_map, avatar_name)
        except AuthenticationRequiredError:
            vrchat_api.authenticate(login, password)
        except AvatarNotFoundError as error:
            logger.error(error)


if __name__ == "__main__":
    console_switch()
