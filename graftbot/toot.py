from mastodon import Mastodon

import graftbot.dirs


def toot(api_base_url: str, tootstr: str) -> int:
    mastodon = Mastodon(
        client_id=graftbot.dirs.client_file(),
        access_token=graftbot.dirs.user_file(),
        api_base_url=api_base_url,
    )
    mastodon.toot(tootstr)
    return 0
