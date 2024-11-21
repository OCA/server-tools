# pylint: disable=invalid-name,print-used
import json

import requests
from api_login import get_args, get_config, get_session


def template_get(args, config, cookies):
    """Retrieve subscription information"""
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
            "params": {"xmlid": args.xmlid, "language": args.language},
            "id": "template_get",
        }
    )
    response = requests.get(
        url=endpoint, headers=headers, data=json_data, cookies=cookies, timeout=15
    )
    received = response.json()
    if "result" in received:
        print(received["result"]["template_content"])  # to stdout
    else:
        print(response.text)


if __name__ == "__main__":
    main_args = get_args()
    main_config = get_config()
    main_cookies = get_session(main_args, main_config)
    template_get(main_args, main_config, main_cookies)
