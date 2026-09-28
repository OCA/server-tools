# pylint: disable=invalid-name,print-used
import json

import requests
from api_login import get_args, get_config, get_session


def template_list_receive(args, cookies=None):
    """Retrieve subscription information"""
    config = get_config()
    cookies = cookies or get_session(args, config)
    config_dict = config["template_list"]
    endpoint = "%s/" % config_dict["endpoint"]
    headers = {"Content-Type": "application/json"}
    # Accepted parameters:
    # module: name
    json_data = json.dumps(
        {
            "jsonrpc": "2.0",
            "params": {"module": args.module},
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


def template_list(args):
    received = template_list_receive(args)
    template_list = received["result"]["template_list"]
    for xmlid in template_list:
        print("%s.%s" % (args.module, xmlid))  # to stdout


if __name__ == "__main__":
    main_args = get_args()
    template_list(main_args)
