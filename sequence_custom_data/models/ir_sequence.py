# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, exceptions, models

_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    """
    Inherit standard ir.sequence to let the possibility of using others variables than
    ones defined by Odoo.
    To allow this, you only have to inherit this model and update dict returned by the
    function _get_special_values(...).
    Example:
        class IrSequence(models.Model):
        _inherit = "ir.sequence"

        def _get_special_values(self, date=None, date_range=None):
            values = super()._get_special_values(date=date, date_range=date_range)
            company_code = self.env.company.special_code
            values.update({"company_code": company_code or ""})
            return values

    The prefix/suffix into the sequence should be in this format:
    - {company_code}ABC
    - %(year)s{company_code}
    - {company_code}
    """

    _inherit = "ir.sequence"

    def _get_special_values(self, date=None, date_range=None):
        """
        Get the dict with custom values to use into prefix/suffix.
        The expected code format into the prefix/suffix is not the same than Odoo.
        You should use {my_code} who will be replaced by the value into the dict.
        :return: dict
        """
        return {}

    def _get_prefix_suffix(self, date=None, date_range=None):
        """
        Inherit to let the possibility to add custom values to replace into
        generated prefix/suffix.
        As it's not possible to add (easily) variables with the same format than
        standard (and to avoid exception during replacement), the format must be
        different.
        The format (into prefix/suffix) is the one used of format(...) on a string.
        Ex:
        "Sequence-{variable1}".format(variable1="test")
        This format is compatible with the standard and doesn't trigger any known issue.
        :param date:
        :param date_range:
        :return: str, str
        """
        interpolated_prefix, interpolated_suffix = super()._get_prefix_suffix(
            date=date, date_range=date_range
        )
        special_values = self._get_special_values(date=date, date_range=date_range)
        if special_values:
            try:
                interpolated_prefix = interpolated_prefix.format(**special_values)
                interpolated_suffix = interpolated_suffix.format(**special_values)
            except KeyError as e:
                _logger.error(e)
                msg = _(
                    "An error appears during the generation of the sequence "
                    "(code: {code}).\n"
                    "Please check prefix and suffix with available values."
                ).format(code=self.code)
                raise exceptions.UserError(msg) from e
        return interpolated_prefix, interpolated_suffix
