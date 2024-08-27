"""Basic script to switch avatars using the console.

Provide VRChat credentials via environment variables:
LOGIN={login}
PASSWORD={password}
MFA_CODE={code}
And type the name of the avatar to change to. Partial match. Chooses from all favorites avatars
"""
import logging
import os

from avatar_switch.avatar_switcher import AvatarSwitcher
from avatar_switch.vrchat_api import VRChatAPI


def console_switch():
    """Switch VRChat avatars using the console"""
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    mfa_code = os.getenv("MFA_CODE")

    vrchat_api = VRChatAPI()
    vrchat_api.basic_authentication(login, password)
    vrchat_api.mfa_authentication(mfa_code)
    avatar_switcher = AvatarSwitcher(vrchat_api)
    avatars_map = avatar_switcher.get_all_favorite_avatars()
    while True:
        avatar_name = input("Waiting for avatar name: ")
        avatar_switcher.switch_avatar_by_name(avatars_map, avatar_name)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    console_switch()