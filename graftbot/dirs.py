import os


_cfgdir = "~/.graftbot/mastodon"
_clientfile = "clientcred.secret"
_userfile = "usercred.secret"
_lastnotiffile = "last_notif"


def config_dir() -> str:
    return os.path.expanduser(_cfgdir)


def client_file() -> str:
    return os.path.join(config_dir(), _clientfile)


def user_file() -> str:
    return os.path.join(config_dir(), _userfile)


def last_notif_file() -> str:
    return os.path.join(config_dir(), _lastnotiffile)


def raw_config_dir() -> str:
    return _cfgdir


def raw_client_file() -> str:
    return os.path.join(raw_config_dir(), _clientfile)


def raw_user_file() -> str:
    return os.path.join(raw_config_dir(), _userfile)
