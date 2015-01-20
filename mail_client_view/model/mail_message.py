# -*- coding: UTF-8 -*-
'''
Created on 16 apr. 2013

@author: Therp BV

http://www.therp.nl
'''
from openerp.osv.orm import Model
from openerp.osv import fields


class mail_message(Model):
    '''Extend mail_message with action_needed flag'''
    _inherit = 'mail.message'

    def set_action_needed_off(self, cr, user, ids, context=None):
        self.write(cr, user, ids, {'action_needed': False}, context=context)
        return True

    def set_action_needed_on(self, cr, user, ids, context=None):
        self.write(cr, user, ids, {'action_needed': True}, context=context)
        return True

    def create(self, cr, user, vals, context=None):
        # Set newly received messages as needing action, unless an
        # explicit value for action_needed has been passed.
        if ('action_needed' not in vals
                and ('state' in vals) and (vals['state'] == 'received')):
            vals['action_needed'] = True
        mm_id = super(mail_message, self).create(
            cr, user, vals, context=context)
        return mm_id

    _columns = {
        'action_needed': fields.boolean(
            'Action needed',
            help='Action needed is True whenever a new mail is received, or'
                 ' when a user flags a message as needing attention.'),
    }
