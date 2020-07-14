It will be necessary to create an app at https://api.slack.com/apps/ in the workspace that we want to work and define it by name: Odoo and the scopes: channels: read + chat: write

For the correct functioning of Slack in the channels, it will be necessary that within the channel, in "More" click on "Add applications" and we have added the previously created Odoo application.

You will need to add the following to the odoo.conf file
slack_bot_user_oauth_access_token=xxxxx

It will be necessary to configure the ir config parameter with the key slack_log_channel + slack_log_ses_mail_tracking_channel (for example #channel_odoo) which will be the Slack channel to which notifications will be sent
