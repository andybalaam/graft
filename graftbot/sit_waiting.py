from datetime import datetime, timezone
import os
import re
import time

from mastodon import Mastodon

import graftlib
import graftbot.dirs
from graftbot.strip_html import strip_html
from graftlib.world import World


def _check_for_unseen_notifications(world, mastodon):
    last_notif = world.fs.read_file_or_none(graftbot.dirs.last_notif_file())
    return mastodon.notifications(since_id=last_notif)


def _update_last_notif(world, id_):
    world.fs.write_file(graftbot.dirs.last_notif_file(), str(id_))


def _make_gif(world, program):
    os.makedirs("bot-gifs", exist_ok=True)

    gif_file = os.path.join("bot-gifs", "gif-{}.gif".format(
        datetime.now(tz=timezone.utc).isoformat()))

    argv = ["./graft", "--gif", gif_file, "--frames", "100", program]
    world.stdout.write(" ".join(argv) + "\n")

    lib_world = World(
        argv=argv,
        stdin=None,
        stdout=world.stdout,
        stderr=world.stderr,
        random=world.random,
        fs=world.fs
        )
    graftlib.main.main(lib_world)
    return gif_file


def _follow(mastodon, acct):
    mastodon.follows(acct)


def _post_gif(mastodon, gif_file, program, acct):
    media = mastodon.media_post(
        gif_file,
        description="Graft program '{program}' by @{acct}".format(
            program=program,
            acct=acct,
        ),
    )
    return media["id"]


def _post_toot(mastodon, status_id, media_id, program, acct):
    new_status = mastodon.status_post(
        status="'{program}' by @{acct}".format(
            program=program,
            acct=acct,
        ),
        in_reply_to_id=status_id,
        media_ids=[media_id],
    )
    return new_status["id"]


def _post_error_toot(mastodon, status_id, error, program, acct):
    new_status = mastodon.status_post(
        status="@{acct} Error: '{error}' in program '{program}'".format(
            acct=acct,
            error=error,
            program=program,
        ),
        in_reply_to_id=status_id,
    )
    return new_status["id"]


whitespace_re = re.compile(r"\s")


def _run_and_toot(world, mastodon, n):
    acct = n["account"]["acct"]
    toot = strip_html(n["status"]["content"])
    status_id = n["status"]["id"]
    program = whitespace_re.sub("", toot.replace("@graft", ""))

    _follow(mastodon, acct)

    world.stdout.write(
        "Processing notification {notif_id} from @{acct}: '{toot}'\n".format(
            notif_id=n["id"],
            acct=acct,
            toot=toot,
            )
    )

    try:
        gif_file = _make_gif(world, program)
    except Exception as e:
        world.stdout.write("Error running program: {}\n".format(str(e)))
        world.stdout.write("Tooting error back.\n")
        new_status_id = _post_error_toot(
            mastodon, status_id, str(e), program, acct)
        world.stdout.write("Toot {} posted.\n\n".format(new_status_id))
        return

    world.stdout.write("Uploading {}\n".format(gif_file))

    media_id = _post_gif(mastodon, gif_file, program, acct)

    world.stdout.write("Tooting media id {}\n".format(media_id))

    new_status_id = _post_toot(mastodon, status_id, media_id, program, acct)

    world.stdout.write("Toot {} posted.\n\n".format(new_status_id))


def _run_and_toot_first(world, mastodon, notifs):
    for n in notifs:
        if n["type"] != "mention":
            _update_last_notif(world, n["id"])
        else:
            _run_and_toot(world, mastodon, n)
            _update_last_notif(world, n["id"])
            break  # Only do one at a time


def sit_waiting(world: World, api_base_url: str) -> int:
    mastodon = Mastodon(
        client_id=graftbot.dirs.client_file(),
        access_token=graftbot.dirs.user_file(),
        api_base_url=api_base_url,
    )

    while True:
        try:
            notifs = _check_for_unseen_notifications(world, mastodon)
            if notifs:
                _run_and_toot_first(world, mastodon, notifs)
        except Exception as e:
            world.stderr.write("{}\n\n".format(str(e)))
        time.sleep(60)

    return 0
