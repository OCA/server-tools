# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 solutions2use (<http://www.solutions2use.com>)
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import argparse
from oauth2client import file
from oauth2client import client
from oauth2client import tools


class GoogleApiAccount(orm.Model):

    _name = 'google.api.account'
    _columns = {
        'name': fields.char('Account', size=50, required=True),
        'secrets_path': fields.char('Secrets path', size=100, required=True),
        'credential_path': fields.char(
            'Credential path', size=100, required=True),
        'synchronize': fields.boolean('Auto synchronize'),
        'use_local_browser': fields.boolean(
            'Use local browser',
            help="""If you can not run a local browser on the machine where
            Odoo-Server is running on, please deactivate this option.
            For getting authorized you must start Odoo-Server in
            interactive mode. After clicking on 'Authorize' you willbe asked
            to enter a verification code."""
        ),
    }

    _defaults = {
        'secrets_path': 'client_secrets.json',
        'credential_path': 'credentials.dat',
        'synchronize': True,
        'use_local_browser': True,
    }

    def do_authorize(self, cr, uid, ids, context=None):

        account = self.browse(cr, uid, ids[0])

        FLOW = client.flow_from_clientsecrets(
            account.secrets_path,
            scope=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.readonly',
                'https://www.google.com/m8/feeds',
            ],
            message=tools.message_if_missing(account.secrets_path)
        )

        storage = file.Storage(account.credential_path)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[tools.argparser]
            )
            if not account.use_local_browser:
                flags = parser.parse_args(['--noauth_local_webserver'])
            else:
                flags = parser.parse_args([])
            credentials = tools.run_flow(FLOW, storage, flags)

        raise orm.except_orm(
            _(u'Done.'),
            _(u'Please verify if your credential file is created or updated.'))
