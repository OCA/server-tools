# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm
from openerp.tools.translate import _
import logging

logger = logging.getLogger(__name__)


class IrCron(orm.Model):
    _name = 'ir.cron'
    _inherit = ['ir.cron', 'mail.thread']

    def _handle_callback_exception(self, cr, uid, model_name, method_name,
                                   args, job_id, job_exception):

        res = super(IrCron, self)._handle_callback_exception(
            cr, uid, model_name, method_name, args, job_id, job_exception)

        my_cron = self.browse(cr, uid, job_id)

        self.message_post(
            cr, uid, [my_cron.id],
            body=_('An error occured during execution of cron'
                   ' %s on DB %s:\n%s') % (my_cron.name, cr.dbname,
                                           job_exception))

        logger.debug("Posting scheduler error mail with error:%s",
                     job_exception)

        return res
