# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, tools
_logger = logging.getLogger(__name__)

try:
    import slack
except (ImportError, IOError) as err:
    _logger.debug(err)


class SlackMessage(models.Model):
    _name = 'slack.message'
    _description = 'Slack Message'

    @api.model
    def create(self, values):
        channel = self.env['ir.config_parameter'].sudo().get_param('slack_log_channel')
        api_token = tools.config.get('slack_bot_user_oauth_access_token')
        if api_token is not None:
            # api_token
            if 'api_token' in values:
                api_token = values['api_token']
            # default
            msg = ''
            attachments = []
            # msg
            if 'msg' in values:
                msg = values['msg']
            # attachments
            if 'attachments' in values:
                attachments = values['attachments']
            # channel
            if 'channel' in values:
                channel = values['channel']
            # SlackClient
            try:
                sc = slack.WebClient(token=api_token)
                result = sc.chat_postMessage(
                    channel=channel,
                    text=msg,
                    attachments=attachments,
                    username='Odoo'
                )
                if 'error' in result:
                    _logger.debug({
                        'channel': channel,
                        'error': result['error']
                    })
            except:
                _logger.debug('Slack Error')
            # return
            return False
