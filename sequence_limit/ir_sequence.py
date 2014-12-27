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
from openerp.osv import orm, fields
from tools.translate import _


class IrSequence(orm.Model):
    _inherit = "ir.sequence"

    _columns = {
        'number_max': fields.integer(
            'Max Number',
            help="the maximum number for the sequence being"),
        'number_max_warning_before': fields.integer(
            'Warning Before Max Number',
            help="the number before reaching the limit to display an alert"),
        'number_warning_active': fields.selection([
            ('no-message', 'No Message'),
            ('warning', 'Warning'),
        ],
            'To Activate The Warning',
            help=('Selecting the "Warning" option will notify user with'
                  'a message.')),
        'limit_date': fields.date(
            'Limit Date',
            help="the deadline for the sequence being"),
        'limit_date_warning_before': fields.date(
            'Warning Date Before Limit Date',
            help="the date before reaching the limit to display an alert"),
        'date_warning_active': fields.selection([
            ('no-message', 'No Message'),
            ('warning', 'Warning'),
        ],
            'To Activate The Warning',
            help=('Selecting the "Warning" option will notify user with'
                  'a message.')),
    }

    _defaults = {
        'number_max': '0',
        'number_max_warning_before': '0',
        'number_warning_active': 'no-message',
        'date_warning_active': 'no-message',
    }

    def _next(self, cr, uid, seq_ids, context=None):
        user_obj = self.pool.get("res.users")
        model_data_obj = self.pool.get("ir.model.data")
        seq_id = self.get_sequence_id(cr, uid, seq_ids, context=context)
        sequence = self.browse(cr, uid, seq_id, context=context)
        result_next = super(IrSequence, self)._next(
            cr, uid, seq_ids, context=context)
        if (sequence.number_max != 0 and sequence.number_warning_active == 'warning') \
                or (sequence.limit_date and sequence.date_warning_active == 'warning'):
            result_max = self._build_sequence_number(
                cr, uid, sequence, sequence.number_max, context=context)
            result_before_max = self._build_sequence_number(
                cr, uid,
                sequence,
                sequence.number_max_warning_before,
                context=context)
            user = user_obj.browse(cr, uid, uid, context=context)
            if result_max <= result_next and sequence.number_max != 0:
                message_number_max = _("The number max: %s was reached "
                                       "for the sequence: %s."
                                       "(Contact the Administrator please.)") \
                    % (result_max, sequence.name)
                raise orm.except_orm(
                    _('Warning.'), message_number_max)
            elif sequence.limit_date <= fields.date.today() \
                    and sequence.limit_date:
                message_deadline = _("The deadline: %s was reached "
                                     "for the sequence: %s."
                                     "(Contact the Administrator please .)") \
                    % (sequence.limit_date, sequence.name)
                raise orm.except_orm(
                    _('Warning.'), message_deadline)
            elif result_before_max == result_next \
                    or fields.date.today() == sequence.limit_date_warning_before:
                message_before_max = _("Warning: you will soon reach "
                                       "the limit of the sequence: %s, "
                                       "current number: %s, max number: %s") \
                    % (sequence.name, result_next, result_max)
                message_before_deadline = _("Warning: you will soon reach "
                                            "the limit of the sequence: %s, "
                                            "current date: %s, "
                                            "deadline: %s") \
                    % (sequence.name, fields.date.today(), sequence.limit_date)
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
                    self.send_warning_message(cr, uid,
                                              partner_ids,
                                              sequence,
                                              result_next,
                                              result_before_max,
                                              message_before_max,
                                              message_before_deadline,
                                              context=context)
        return result_next

    def _build_sequence_number(self, cr, uid, sequence, number, context=None):
        d = self._interpolation_dict()
        interpolated_prefix = self._interpolate(sequence.prefix, d)
        interpolated_suffix = self._interpolate(sequence.suffix, d)
        sequence = '%0*d' % (sequence.padding, number)
        return '%s%s%s' % (interpolated_prefix, sequence, interpolated_suffix)

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
        preferred_sequence = sequences[0]
        for seq in sequences:
            if seq['company_id'] and seq['company_id'] == force_company:
                preferred_sequence = seq
                break
        return preferred_sequence['id']

    def send_warning_message(self, cr, uid,
                             partner_ids, sequence, result_next,
                             result_before_max, message_before_max,
                             message_before_deadline, context=None):
        mail_thread_obj = self.pool.get('mail.thread')
        if result_before_max == result_next:
            mail_thread_obj.message_post(
                cr, uid,
                False,
                body=message_before_max,
                #partner_ids=[(6, 0, partner_ids)],
                context=context)
        elif fields.date.today() == sequence.limit_date_warning_before:
            mail_thread_obj.message_post(
                cr, uid,
                False,
                body=message_before_deadline,
                #partner_ids=[(6, 0, partner_ids)],
                context=context)
            return True
