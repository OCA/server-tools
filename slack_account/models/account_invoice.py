# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one    
    def action_auto_create_message_slack(self):
        res = super(AccountInvoice, self).action_auto_create_message_slack()
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                                        
        attachments = [
            {
                "title": _("Invoice has been created automatically"),
                "text": self.number,
                "fallback": _("View invoice ")+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.invoice",
                "color": "#36a64f",
                "actions": [
                    {
                        "type": "button",
                        "text": _("View invoice"),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.invoice"
                    }
                ],
                "fields": [                    
                    {
                        "title": _("Customer"),
                        "value": self.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Amount"),
                        "value": str(self.amount_total)+' '+self.currency_id.symbol,
                        'short': True,
                    }
                ],
            }
        ]
        
        slack_message_vals = {
            'attachments': attachments,
            'model': 'account.invoice',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_contabilidad_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res            