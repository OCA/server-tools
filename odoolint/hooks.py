# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import imp
import logging
from contextlib import contextmanager

from openerp import tools

_logger = logging.getLogger(__name__)


DATA_FILE_NAME = None
DATA_FILE_SECTION = None
DATA_FILE_MODULE = None


@contextmanager
def file_info(filename, filesection, filemodule):
    """Change the file_info temporally
    """
    # pylint: disable=global-statement
    global DATA_FILE_NAME
    global DATA_FILE_SECTION
    global DATA_FILE_MODULE
    DATA_FILE_NAME = filename
    DATA_FILE_SECTION = filesection
    DATA_FILE_MODULE = filemodule
    try:
        yield
    finally:
        DATA_FILE_NAME = None
        DATA_FILE_SECTION = None
        DATA_FILE_MODULE = None


def get_file_info():
    """Return dictionary with file_name, section of file and module real name
    """
    return {
        'file_name': DATA_FILE_NAME,
        'section': DATA_FILE_SECTION,
        'module_real': DATA_FILE_MODULE,
    }


def monkey_patch_convert_file():
    """Monkey patch to openerp.tools.convert.convert_file method to add custom
    information for importation process.
    """
    convert_file_original = tools.convert.convert_file

    def convert_file(*args, **kwargs):
        module = args[1]
        filename = args[2]
        section = args[6]
        # print args, kwargs
        with file_info(filename, section, module):
            return convert_file_original(*args, **kwargs)
    tools.convert.convert_file = convert_file
    # Reload to propagate patch
    imp.reload(tools)


def post_load():
    _logger.info('Patching openerp.tools.convert.convert_file method')
    monkey_patch_convert_file()
