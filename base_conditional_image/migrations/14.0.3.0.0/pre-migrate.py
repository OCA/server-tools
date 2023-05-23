# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migrating conditional image's model names to model records")
    cr.execute(
        """
ALTER TABLE conditional_image ADD COLUMN model_name_old TEXT;
UPDATE conditional_image SET model_name_old = model_name;
    """
    )
