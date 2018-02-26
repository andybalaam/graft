from argparse import ArgumentParser

import graftbot.dirs
from graftbot.log_in import log_in
from graftbot.register_app import register_app
from graftbot.toot import toot
from graftbot.sit_waiting import sit_waiting
from graftlib.world import World


api_base_url = 'https://mastodon.social'


def main(world: World) -> int:
    """Run the Mastodon bot"""

    argparser = ArgumentParser(prog='bot-mastodon')
    argparser.add_argument(
        '--register-app',
        action="store_true",
        help=(
            "ONLY DO THIS ONCE - register this app with mastodon.social.  " +
            "The client secret will be stored in " +
            graftbot.dirs.raw_client_file()
        ),
    )
    argparser.add_argument(
        '--user',
        help=(
            "The username of the user on mastodon.social.  You must provide" +
            " this and --password the first time you run.  The credentials" +
            " will be stored in " +
            graftbot.dirs.raw_user_file()
        ),
    )
    argparser.add_argument(
        '--password',
        help=(
            "The password of the user on mastodon.social."
        ),
    )
    argparser.add_argument(
        '--toot',
        help=(
            "Toot something!"
        ),
    )

    args = argparser.parse_args(world.argv[1:])

    if args.register_app:
        return register_app(world, api_base_url)

    if args.user:
        if not args.password:
            world.stderr.write(
                "You must supply --password if you supply --user\n")
            return 2
        else:
            return log_in(api_base_url, args.user, args.password)
    elif args.password:
        world.stderr.write(
            "You must supply --user if you supply --password\n")
        return 2

    if args.toot:
        return toot(api_base_url, args.toot)

    return sit_waiting(world, api_base_url)
