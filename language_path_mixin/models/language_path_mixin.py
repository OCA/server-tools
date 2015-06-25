# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, an open source suite of business apps
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp import models


class LanguagePathMixin(models.AbstractModel):
    """ Mixin class to print reports in a language taken from a field in the
    record. """
    _name = 'language.path.mixin'
    _language_path = False

    def with_language_path(self, path=None):
        """ This method allows the system to iterate over a RecordSet with each
        of the records being browsed in the language specified by the model's
        _language_path attribute. Of course, this is a cache killer. It was
        conceived to make translations in rml reports work again as using
        setLang() in the report does not work as expected anymore in 8.0 due
        to the way that caching works in the new API """
        path = path or self._language_path
        for record in self:
            if not path:
                yield record
                continue
            lang = record
            for part in path.split('.'):
                lang = lang[part]
                if not lang:
                    yield record
                    break
            else:
                yield record.with_context(lang=lang)
