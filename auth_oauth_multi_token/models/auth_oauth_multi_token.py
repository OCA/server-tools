# -*- coding: utf-8 -*-
# Florent de Labarre - 2016

from openerp import api, fields, models


class auth_oauth_multi_token(models.Model):
    """Class defining list of tokens"""

    _name = 'auth.oauth.multi.token'
    _description = 'OAuth2 token'
    _order = "id desc"

    oauth_access_token = fields.Char('OAuth Access Token', readonly=True, copy=False)
    user_id = fields.Many2one('res.users', 'User', required=True)
    active_token = fields.Boolean('Active')

    @api.model
    def create(self, vals):
        res = super(auth_oauth_multi_token, self).create(vals)
        oauth_access_token_ids = self.search([('user_id', '=', vals['user_id']), ('active_token', '=', True)], ).ids
        oauth_access_max_token = self.env['res.users'].search([('id', '=', vals['user_id'])], limit=1).oauth_access_max_token
        if len(oauth_access_token_ids) >= oauth_access_max_token:
            self.browse(oauth_access_token_ids[oauth_access_max_token]).write({
                'oauth_access_token': "****************************",
                'active_token': False})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
