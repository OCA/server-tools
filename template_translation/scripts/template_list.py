# pylint: disable=invalid-name,print-used
import json

import requests
from api_login import get_args, get_config, get_session


def template_list(args, config, cookies):
    """Retrieve subscription information"""
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
    if "result" in received:
        template_list = received["result"]["template_list"]
        for xmlid in template_list:
            print("%s.%s" % (args.module, xmlid))  # to stdout
    else:
        print(response.text)


if __name__ == "__main__":
    main_args = get_args()
    main_config = get_config()
    main_cookies = get_session(main_args, main_config)
    template_list(main_args, main_config, main_cookies)
