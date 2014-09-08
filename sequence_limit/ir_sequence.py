# -*- encoding: utf-8 -*-
###############################################################################
#
#  sequence_limit for OpenERP
#   Copyright (C) 2012-14 Akretion Chafique DELLI <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import osv
from osv import orm, fields
from tools.translate import _


class IrSequence(orm.Model):
    _inherit = "ir.sequence"

    _columns = {
        'number_max': fields.integer(
            'Max Number',
            help="the maximum number for the sequence being"),
        'number_max_warn_bfr': fields.integer(
            'Warning Before Max Number',
            help="the number before reaching the limit to display an alert"),
        'number_warn_active': fields.selection([
            ('no-message', 'No Message'),
            ('warning', 'Warning'),
        ],
            'To Activate The Warning',
            help=('Selecting the "Warning" option will notify user with'
                  'a message.')),
        'limit_dat': fields.date(
            'Limit Date',
            help="the deadline for the sequence being"),
        'limit_dat_warn_bfr': fields.date(
            'Warning Date Before Limit Date',
            help="the date before reaching the limit to display an alert"),
        'dat_warn_active': fields.selection([
            ('no-message', 'No Message'),
            ('warning', 'Warning'),
        ],
            'To Activate The Warning',
            help=('Selecting the "Warning" option will notify user with'
                  'a message.')),

    }

    _defaults = {
        'number_max': '0',
        'number_max_warn_bfr': '0',
        'number_warn_active': 'no-message',
        'dat_warn_active': 'no-message',
    }

    def _next(self, cr, uid, seq_ids, context=None):
        mail_thread_obj = self.pool.get('mail.thread')
        user_obj = self.pool.get("res.users")
        model_data_obj = self.pool.get("ir.model.data")
        seq_id = self.get_sequence_id(cr, uid, seq_ids, context=context)
        sequence = self.browse(cr, uid, seq_id, context=context)
        result_next = super(IrSequence, self)._next(
            cr, uid, seq_ids, context=context)
        if (sequence.number_max != 0 \
            and sequence.number_warn_active == 'warning') \
            or (sequence.limit_dat \
                and sequence.dat_warn_active == 'warning'):
            result_max = self._build_sequence_number(
                cr, uid, sequence, sequence.number_max, context=context)
            result_bfr_max = self._build_sequence_number(
                cr, uid,
                sequence,
                sequence.number_max_warn_bfr,
                context=context)
            user = user_obj.browse(cr, uid, uid, context=context)
            if result_max <= result_next and sequence.number_max != 0:
                message_number_max = _("""The number max: %s was reached for the sequence: %s."""
                                       """(Contact the Administrator please !)""") \
                    % result_max % sequence.name
                raise osv.except_osv(
                    _('Alert for %s !') % user.name, message_number_max)
            elif sequence.limit_dat <= fields.date.today() \
                    and sequence.limit_dat:
                message_deadline = _("""The deadline: %s was reached for the sequence: %s."""
                                     """(Contact the Administrator please !)""") \
                    % sequence.limit_dat % sequence.name
                raise osv.except_osv(
                    _('Alert for %s !') % user.name, message_deadline)
            elif result_bfr_max == result_next \
                    or fields.date.today() == sequence.limit_dat_warn_bfr:
                msg_bfr_max = _("""Warning: you will soon reach the limit of the sequence: %s, """
                                """current number: %s, max number: %s""") \
                    % sequence.name % result_next % result_max
                msg_bfr_deadline = _("""Warning: you will soon reach the limit of the sequence: %s, """
                                     """current date: %s, """
                                     """deadline: %s""") \
                    % sequence.name % fields.date.today() % sequence.limit_dat
                model, group_id = model_data_obj.get_object_reference(
                    cr, uid, 'base', 'group_system')
                user_ids = user_obj.search(
                    cr, uid,
                    [('groups_id', '=', group_id)],
                    context=context)
                users = user_obj.browse(cr, uid, user_ids, context=context)
                partner_ids = []
                for user in users:
                    partner_ids.append(user.partner_id.id)
                if result_bfr_max == result_next:
                    mail_thread_obj.message_post(
                        cr, uid,
                        False,
                        msg_bfr_max,
                        partner_ids=[(6, 0, partner_ids)],
                        subtype='sequence_limit.notify',
                        context=context)
                elif fields.date.today() == sequence.limit_dat_warn_bfr:
                    mail_thread_obj.message_post(
                        cr, uid,
                        False,
                        msg_bfr_deadline,
                        partner_ids=[(6, 0, partner_ids)],
                        subtype='sequence_limit.notify',
                        context=context)
        return result_next

    def _build_sequence_number(self, cr, uid, sequence, number, context=None):
        d = self._interpolation_dict()
        interpolated_prefix = self._interpolate(sequence.prefix, d)
        interpolated_suffix = self._interpolate(sequence.suffix, d)
        return interpolated_prefix \
            + '%%0%sd' % sequence.padding % number \
            + interpolated_suffix

    def get_sequence_id(self, cr, uid, seq_ids, context=None):
        if context is None:
            context = {}
        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(
                cr, uid, uid).company_id.id
        sequences = self.read(
            cr, uid,
            seq_ids,
            [
                'company_id',
                'implementation',
                'number_next',
                'prefix',
                'suffix',
                'padding'
                ])
        preferred_sequences = [s for s in sequences if s['company_id'] and \
                               s['company_id'][0] == force_company ]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        return seq['id']
