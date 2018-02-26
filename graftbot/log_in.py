from mastodon import Mastodon

import graftbot.dirs


def log_in(api_base_url: str, user: str, password: str) -> int:
    mastodon = Mastodon(
        client_id=graftbot.dirs.client_file(),
        api_base_url=api_base_url,
    )
    mastodon.log_in(
        user,
        password,
        to_file=graftbot.dirs.user_file()
    )
    return 0
