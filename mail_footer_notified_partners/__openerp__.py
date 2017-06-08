# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_footer_notified_partners,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_footer_notified_partners is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_footer_notified_partners is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_footer_notified_partners.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Mail Footer Notified Partners",
    'summary': """
        This module adds the list of notified partners in the footer of
        notification e-mails sent by Odoo.
        """,
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Mail',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
    ],
}
