# pylint: disable=invalid-name,print-used
import json
import sys

import requests
from api_login import get_args, get_config, get_session


def template_put(args, config, cookies):
    """Put content back in xmlid"""
    template_content = sys.stdin.readlines()
    config_dict = config["template_put"]
    endpoint = "%s" % config_dict["endpoint"]
    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(
        {
            "jsonrpc": "2.0",
            "params": {
                "xmlid": args.xmlid,
                "language": args.language,
                "template_content": "\n".join(template_content),
            },
            "id": "template_put",
        }
    )
    response = requests.post(
        url=endpoint, headers=headers, data=json_data, cookies=cookies, timeout=15
    )
    if "result" not in response:
        print(response.text)


if __name__ == "__main__":
    main_args = get_args()
    main_config = get_config()
    main_cookies = get_session(main_args, main_config)
    template_put(main_args, main_config, main_cookies)
