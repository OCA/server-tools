# -*- encoding: utf-8 -*-
# Copyright 2015 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
import logging
import pytz
from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)


class IrQweb(models.Model):
    _inherit = 'ir.qweb'

    def render_tag_usertime(self, element, template_attributes,
                            generated_attributes, qwebcontext):
        tformat = template_attributes['usertime']
        if not tformat:
            # No format, use default time and date formats from qwebcontext
            lang = (
                qwebcontext['env'].lang or
                qwebcontext['env'].context['lang'] or
                qwebcontext['user'].lang
            )
            if lang:
                lang = qwebcontext['env']['res.lang'].search(
                    [('code', '=', lang)]
                )
                tformat = "{0.date_format} {0.time_format}".format(lang)
            else:
                tformat = DEFAULT_SERVER_DATETIME_FORMAT

        now = datetime.now()

        tz_name = qwebcontext['user'].tz
        if tz_name:
            try:
                utc = pytz.timezone('UTC')
                context_tz = pytz.timezone(tz_name)
                utc_timestamp = utc.localize(now, is_dst=False)  # UTC = no DST
                now = utc_timestamp.astimezone(context_tz)
            except Exception:
                _logger.debug(
                    "failed to compute context/client-specific timestamp, "
                    "using the UTC value",
                    exc_info=True)
        return now.strftime(tformat)
