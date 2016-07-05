# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

""" QWeb usertime : adds support for t-usertime on qweb reports """

from datetime import datetime
import logging
import pytz

from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class QWeb(models.Model):
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
