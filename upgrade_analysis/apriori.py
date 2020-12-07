""" Encode any known changes to the database here
to help the matching process
"""

import logging

_logger = logging.getLogger(__name__)


try:
    from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules
except ImportError:
    renamed_modules = {}
    merged_modules = {}
    _logger.warning(
        "You are using upgrade_analysis without having"
        " openupgrade_scripts module available."
        " The analysis process will not work properly,"
        " if you are generating analysis for the odoo modules"
        " in an openupgrade context."
    )

renamed_modules.update({})

merged_modules.update({})

# only used here for upgrade_analysis
renamed_models = {}

# only used here for upgrade_analysis
merged_models = {}
