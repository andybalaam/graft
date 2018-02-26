from mastodon import Mastodon

import graftbot.dirs
from graftlib.world import World


def toot(world: World, api_base_url: str, toot: str) -> int:
    mastodon = Mastodon(
        client_id=graftbot.dirs.client_file(),
        access_token=graftbot.dirs.user_file(),
        api_base_url=api_base_url,
    )
    mastodon.toot(toot)
    return 0
