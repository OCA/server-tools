# pylint: disable=invalid-name,print-used
import base64
import datetime
import json

import requests
from api_login import get_args, get_config, get_session


def test_attachments(config, cookies):
    """Create documents with attachment"""
    config_dict = config["attachments"]
    endpoint = "%s" % config_dict["endpoint"]
    result_type_id = int(config_dict["result_type_id"])
    subscription_id = int(config_dict["subscription_id"])
    headers = {"Content-Type": "application/json"}
    with open("40.pdf", "rb") as binary_file:
        datas = base64.b64encode(binary_file.read())
    base64_data = datas.decode()
    json_data = json.dumps(
        {
            "jsonrpc": "2.0",
            "params": {
                "filename": "40.pdf",
                "subscription_id": subscription_id,
                "name": "the name %s" % datetime.datetime.now().isoformat()[:19],
                "type_id": result_type_id,
            },
            "file": base64_data,
            "id": "test_attachments",
        }
    )
    response = requests.post(
        url=endpoint, headers=headers, data=json_data, cookies=cookies, timeout=15
    )
    print(response.text)


if __name__ == "__main__":
    main_args = get_args()
    main_config = get_config()
    main_cookies = get_session(main_args, main_config)
    test_attachments(main_config, main_cookies)
