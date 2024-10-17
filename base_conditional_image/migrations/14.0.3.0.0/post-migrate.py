# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migrating conditional image's model names to model records")
    cr.execute(
        """
UPDATE conditional_image AS ci SET model_id = (
    SELECT id FROM ir_model WHERE model = ci.model_name_old
);
ALTER TABLE conditional_image DROP COLUMN model_name_old;
    """
    )
