# pylint: disable=invalid-name,print-used
import json

import requests
from api_login import get_args, get_config, get_session


def template_get_receive(args, xmlid=None, cookies=None):
    """Retrieve subscription information"""
    config = get_config()
    cookies = cookies or get_session(args, config)
    config_dict = config["template_get"]
    endpoint = "%s/" % config_dict["endpoint"]
    headers = {"Content-Type": "application/json"}
    # Accepted parameters:
    # xmlid: module qualified xmlid of template
    # dbid: id of template in the database
    # language
    json_data = json.dumps(
        {
            "jsonrpc": "2.0",
            "params": {
                "xmlid": xmlid or args.xmlid,
                "language": args.language,
            },
            "id": "template_get",
        }
    )
    response = requests.get(
        url=endpoint, headers=headers, data=json_data, cookies=cookies, timeout=15
    )
    received = response.json()
    if "result" not in received:
        raise Exception(received)
    return received


def template_get(args):
    received = template_get_receive(args)
    print(received["result"]["template_content"])  # to stdout


if __name__ == "__main__":
    main_args = get_args()
    template_get(main_args)
