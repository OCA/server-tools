# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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


from openerp import fields
import base64
from Crypto.Cipher import AES
from Crypto import Random


class CharLower(fields.Char):
    """
    Identical to fields.Char, except lower cased

    :param int size: the maximum size of values stored for that field
    :param translate: whether the value of this field can be translated
    """

    def convert_to_cache(self, value, record, validate=True):
        """
        convert ``value`` to the cache level in ``env``; ``value`` may come
        from an assignment, or have the format of methods
        :meth:`BaseModel.read` or :meth:`BaseModel.write`

        :param record: the target record for the assignment,
            or an empty recordset

        :param bool validate: when True, field-specific validation of
            ``value`` will be performed
        """
        res = super(CharLower, self).convert_to_cache(value, record, validate)
        if not res:
            return res
        return res.lower()
