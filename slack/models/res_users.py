# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    slack_member_id = fields.Char(
        string='Slack Memeber Id'
    )
    slack_mail_message = fields.Boolean( 
        string='Receive email messages'
    )
    
    @api.multi
    def action_test_slack(self):
        if self.slack_member_id!=False:                                        
            attachments = [
                {                    
                    "title": _("This is a user test *%s*") %(self.name),
                    "color": "#36a64f",                                            
                    "text": _("Test message"),
                }
            ]
            slack_message_vals = {
                'attachments': attachments,
                'model': self._inherit,
                'res_id': self.id,            
                'channel': self.slack_member_id                                                          
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)    