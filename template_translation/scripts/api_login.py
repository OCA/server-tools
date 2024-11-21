# pylint: disable=invalid-name,print-used
import argparse
import json
import logging
import os
import sys
from configparser import ConfigParser, ExtendedInterpolation

import requests

# You must initialize logging, otherwise you'll not see debug output.
_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_logger.propagate = False

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Test login to Fairphone Odoo API\n"
            "Example: python test_scripts/test_script.py -p <password>"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        required=True,
        help="The password to login to the database.",
    )
    parser.add_argument(
        "-x",
        "--xmlid",
        dest="xmlid",
        required=False,
        help="xmlid fo mail template to retrieve.",
    )
    parser.add_argument(
        "-l",
        "--language",
        dest="language",
        required=False,
        help="Full ISO language code, like nl_NL or ru_RU.",
    )
    return parser.parse_args()


def get_config():
    """Use ExtendedInterpolation configparser."""
    config = ConfigParser(interpolation=ExtendedInterpolation())
    path_current_directory = os.path.dirname(__file__)
    path_config_file = os.path.join(path_current_directory, "test.ini")
    config.read(path_config_file)
    return config


def get_session(args, config):
    """Get session using configured parameters."""
    login_dict = config["login"]
    url_login = login_dict["url_login"]
    database = login_dict["database"]
    username = login_dict["username"]
    headers = {"Content-Type": "application/json"}
    data_login = {
        "jsonrpc": "2.0",
        "params": {
            "context": {},
            "db": database,
            "login": username,
            "password": args.password,
        },
    }
    response = requests.get(
        url=url_login, data=json.dumps(data_login), headers=headers, timeout=15
    )
    _logger.debug(str(response.text))
    _logger.debug(str(response.cookies.get("session_id")))
    # Authenticate and get session_id from cookies
    session_id = response.cookies.get("session_id")
    # Use this session_id to prove that we are authenticated
    cookies = {"session_id": session_id}
    return cookies


if __name__ == "__main__":
    main_args = get_args()
    main_config = get_config()
    main_cookies = get_session(main_args, main_config)
