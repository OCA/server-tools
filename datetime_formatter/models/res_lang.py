# Copyright 2015, 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Tecnativa, S.L. - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

# Available modes for :param:`.ResLang.datetime_formatter.template`
MODE_DATETIME = "MODE_DATETIME"
MODE_DATE = "MODE_DATE"
MODE_TIME = "MODE_TIME"


class ResLang(models.Model):
    _inherit = "res.lang"

    @api.model
    def best_match(self, lang=None, failure_safe=True):
        """Get best match of current default lang.
        :param str lang:
            If a language in the form of "en_US" is supplied, it will have the
            highest priority.
        :param bool failure_safe:
            If ``False`` and the best matched language is not found installed,
            an exception will be raised. Otherwise, the first installed
            language found in the DB will be returned.
        """
        # Find some installed language, as fallback
        first_installed = self.search([("active", "=", True)], limit=1)
        if not lang:
            lang = (
                # Object's language, if called like
                # ``record.lang.datetime_formatter(datetime_obj)``
                (self.ids and self[0].code)
                or self.env.context.get("lang")
                or self.env.user.lang
                or first_installed.code
            )
        # Get DB lang record
        record = self.search([("code", "=", lang)])
        try:
            record.ensure_one()
        except ValueError as error:
            if not failure_safe:
                raise UserError(
                    _("Best matched language (%s) not found.") % lang
                ) from error
            else:
                record = first_installed
        return record

    @api.model
    def datetime_formatter(
        self, value, lang=None, template=MODE_DATETIME, separator=" ", failure_safe=True
    ):
        """Convert a datetime field to lang's default format.
        :type value: `str`, `float` or `datetime.datetime`
        :param value:
            Datetime that will be formatted to the user's preferred format.
        :param str lang:
            See :param:`lang` from :meth:`~.best_match`.
        :param bool failure_safe:
            See :param:`failure_safe` from :meth:`~.best_match`.
        :param str template:
            Will be used to format :param:`value`. If it is one of the special
            constants :const:`MODE_DATETIME`, :const:`MODE_DATE` or
            :const:`MODE_TIME`, it will use the :param:`lang`'s default
            template for that mode.
        :param str separator:
            Only used when :param:`template` is :const:`MODE_DATETIME`, as the
            separator between the date and time parts.
        """
        # Get the correct lang
        lang = self.best_match(lang)
        # Get the template
        if template in {MODE_DATETIME, MODE_DATE, MODE_TIME}:
            defaults = []
            if "DATE" in template:
                defaults.append(lang.date_format or DEFAULT_SERVER_DATE_FORMAT)
            if "TIME" in template:
                defaults.append(lang.time_format or DEFAULT_SERVER_TIME_FORMAT)
            template = separator.join(defaults)
        # Convert str to datetime objects
        if isinstance(value, str):
            try:
                value = fields.Datetime.to_datetime(value)
            except ValueError:
                # Probably failed due to value being only time
                value = datetime.strptime(value, DEFAULT_SERVER_TIME_FORMAT)
        # Time-only fields are floats for Odoo
        elif isinstance(value, float):
            # Patch values >= 24 hours
            if value >= 24:
                template = template.replace("%H", "%d" % value)
            # Convert to time
            value = (datetime.min + timedelta(hours=value)).time()
        return value.strftime(template)
