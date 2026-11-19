# Copyright 2024 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from api_login import get_args, get_config, get_session
from template_get import template_get_receive
from template_list import template_list_receive

_logger = logging.getLogger(__name__)


def template_write(xmlid, template_content, language=None):
    """Write template contents to export directory.

    Files will get a name according to the format:
    <module>.<name>.<language>.xml
    """
    config = get_config()
    config_dict = config["template_export"]
    export_directory = config_dict["export_directory"]
    os.makedirs(export_directory, exist_ok=True)
    lang = language or "en_US"
    path = os.path.join(export_directory, "%s.%s.xml" % (xmlid, lang))
    with open(path, mode="w") as xmlfile:  # Overwrite any existing content.
        xmlfile.write(template_content)


def template_get_all(args):
    """Export all module texts in language to files in ~/tmp/ directory."""
    config = get_config()
    cookies = get_session(args, config)
    received = template_list_receive(args, cookies=cookies)
    template_list = received["result"]["template_list"]
    for xmlid in template_list:
        # Get template content one by one and write to file.
        complete_xmlid = "%s.%s" % (args.module, xmlid)
        received = template_get_receive(args, xmlid=complete_xmlid, cookies=cookies)
        template_content = received["result"]["template_content"]
        if not template_content:
            _logger.debug("Did not find content for xmlid %s", complete_xmlid)
            continue
        template_write(complete_xmlid, template_content, language=args.language)


if __name__ == "__main__":
    main_args = get_args()
    template_get_all(main_args)
