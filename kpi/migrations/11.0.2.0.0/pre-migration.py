# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

__name__ = "Upgrade kpi to 11.0.2.0.0"
_logger = logging.getLogger(__name__)


def rename_selection_fields(cr):
    _logger.info("Updating selection fields for periodicty_uom in kpi")
    cr.execute(
        """
        UPDATE kpi
        SET periodicity_uom = 'minutes'
        WHERE periodicity_uom = 'minute'
        """)

    cr.execute(
        """
        UPDATE kpi
        SET periodicity_uom = 'hours'
        WHERE periodicity_uom = 'hour'
        """)

    cr.execute(
        """
        UPDATE kpi
        SET periodicity_uom = 'days'
        WHERE periodicity_uom = 'day'
        """)

    cr.execute(
        """
        UPDATE kpi
        SET periodicity_uom = 'weeks'
        WHERE periodicity_uom = 'week'
        """)

    cr.execute(
        """
        UPDATE kpi
        SET periodicity_uom = 'months'
        WHERE periodicity_uom = 'month'
        """)


def migrate(cr, version):
    if not version:
        return
    rename_selection_fields(cr)
