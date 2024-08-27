from typing import Mapping

from avatar_switch.vrchat_api import VRChatAPI


class AvatarSwitcher:
    def __init__(self, api: VRChatAPI) -> None:
        self.api = api

    def switch_avatar_by_name(self, avatars_map: Mapping[str, str], target_avatar_name: str) -> None:
        for avatar_id, avatar_name in avatars_map.items():
            if target_avatar_name.lower() in avatar_name.lower():
                self.api.switch_avatar(avatar_id)
                return
        return

    def get_all_favorite_avatars(self) -> dict[str, str]:
        avatars_response = self.api.get_avatars()
        avatar_id_name_map: dict[str, str] = {}
        if avatars_response.ok:
            for avatar in avatars_response.json():
                avatar_id_name_map[avatar["id"]] = avatar["name"]
        return avatar_id_name_map
