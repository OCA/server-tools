# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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

from datetime import datetime
import logging

import pytz
from jinja2 import contextfilter

from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DTFMT,
    DEFAULT_SERVER_DATE_FORMAT as DFMT,
)
from openerp.addons.email_template import email_template


_logger = logging.getLogger(__name__)


@contextfilter
def format_date(context, dtstr, new_format=None, tz=None):
    if not dtstr:
        return dtstr

    if not new_format:
        if context.get("user") and context["user"].lang:
            user = context["user"]
            lang_obj = user.pool["res.lang"]
            cr, uid = user._cr, user._uid
            lang = lang_obj.search(cr, uid, [
                ('code', '=', user.lang)
            ])
            if lang:
                new_format = lang_obj.browse(cr, uid, lang[0]).date_format

    new_format = new_format or DFMT

    try:
        date = datetime.strptime(dtstr, DTFMT)
    except ValueError:
        # Maybe this is a date, not datetime
        date = datetime.strptime(dtstr, DFMT)
    else:
        # If this was a date, calculating timezones will give unexpected
        # results. Any timezone with a negative offset will be the day
        # before, since (midnight - anything) is the previous day
        if tz:
            tz_name = tz
        elif context.get("user") and context["user"].tz:
            tz_name = context["user"].tz
        else:
            tz_name = context.get("ctx", {}).get("tz")

        if tz_name:
            try:
                utc = pytz.timezone('UTC')
                context_tz = pytz.timezone(tz_name)
                utc_timestamp = utc.localize(date, is_dst=False)
                date = utc_timestamp.astimezone(context_tz)
            except Exception:
                _logger.debug("failed to compute context/client-specific "
                              "timestamp, using the UTC value",
                              exc_info=True)

    return date.strftime(new_format)


email_template.mako_template_env.filters.update(
    format_date=format_date,
)
