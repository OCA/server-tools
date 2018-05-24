# -*- coding: utf-8 -*-
# Copyright 2015 GRAP - Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
from urllib2 import urlopen
from openerp import api, fields, models

GEOLOCALISATION_URL = u"http://ip-api.com/json/{}"

_logger = logging.getLogger(__name__)


class ResAuthenticationAttempt(models.Model):
    _name = 'res.authentication.attempt'
    _order = 'create_date desc'

    login = fields.Char(string='Tried Login', index=True)
    remote = fields.Char(string='Remote IP', index=True)
    result = fields.Selection(
        string='Authentication Result',
        selection=[
            ('successful', 'Successful'),
            ('failed', 'Failed'),
            ('banned', 'Banned'),
        ],
        index=True,
    )
    remote_metadata = fields.Text(
        string="Remote IP metadata",
        compute='_compute_metadata',
        store=True,
        help="Metadata publicly available for remote IP",
    )
    whitelisted = fields.Boolean(
        compute="_compute_whitelisted",
    )

    @api.multi
    @api.depends('remote')
    def _compute_metadata(self):
        for item in self:
            url = GEOLOCALISATION_URL.format(item.remote)
            try:
                res = json.loads(urlopen(url, timeout=5).read())
            except Exception:
                _logger.warning(
                    "Couldn't fetch details from %s",
                    url,
                    exc_info=True,
                )
            else:
                item.remote_metadata = "\n".join(
                    '%s: %s' % pair for pair in res.items())

    @api.multi
    def _compute_whitelisted(self):
        whitelist = self._whitelist_remotes()
        for one in self:
            one.whitelisted = one.remote in whitelist

    @api.model
    def _hits_limit(self, limit, remote, login=None):
        """Know if a given remote hits a given limit.

        :param int limit:
            The maximum amount of failures allowed.

        :param str remote:
            The remote IP to search for.

        :param str login:
            If you want to check the IP+login combination limit, supply the
            login.
        """
        domain = [
            ("remote", "=", remote),
        ]
        if login is not None:
            domain += [("login", "=", login)]
        # Find last successful login
        last_ok = self.search(
            domain + [("result", "=", "successful")],
            order='create_date desc',
            limit=1,
        )
        if last_ok:
            domain += [("create_date", ">", last_ok.create_date)]
        # Count failures since last success, if any
        recent_failures = self.search_count(
            domain + [("result", "!=", "successful")],
        )
        # Did we hit the limit?
        return recent_failures >= limit

    @api.model
    def _trusted(self, remote, login):
        """Checks if any the remote or remote+login are trusted.

        :param str remote:
            Remote IP from which the login attempt is taking place.

        :param str login:
            User login that is being tried.

        :return bool:
            ``True`` means it is trusted. ``False`` means that it is banned.
        """
        # Cannot ban without remote
        if not remote:
            return True
        get_param = self.env["ir.config_parameter"].sudo().get_param
        # Whitelisted remotes always pass
        if remote in self._whitelist_remotes():
            return True
        # Check if remote is banned
        limit = int(get_param("auth_brute_force.max_by_ip", 50))
        if self._hits_limit(limit, remote):
            _logger.warning(
                "Authentication failed from remote '%s'. "
                "The remote has been banned. "
                "Login tried: %r.",
                remote,
                login,
            )
            return False
        # Check if remote + login combination is banned
        limit = int(get_param("auth_brute_force.max_by_ip_user", 10))
        if self._hits_limit(limit, remote, login):
            _logger.warning(
                "Authentication failed from remote '%s'. "
                "The remote and login combination has been banned. "
                "Login tried: %r.",
                remote,
                login,
            )
            return False
        # If you get here, you are a good boy (for now)
        return True

    def _whitelist_remotes(self):
        """Get whitelisted remotes.

        :return set:
            Remote IPs that are whitelisted currently.
        """
        whitelist = self.env["ir.config_parameter"].sudo().get_param(
            "auth_brute_force.whitelist_remotes",
            "",
        )
        return set(whitelist.split(","))

    @api.multi
    def action_whitelist_add(self):
        """Add current remotes to whitelist."""
        whitelist = self._whitelist_remotes()
        whitelist |= set(self.mapped("remote"))
        self.env["ir.config_parameter"].set_param(
            "auth_brute_force.whitelist_remotes",
            ",".join(whitelist),
        )

    @api.multi
    def action_whitelist_remove(self):
        """Remove current remotes from whitelist."""
        whitelist = self._whitelist_remotes()
        whitelist -= set(self.mapped("remote"))
        self.env["ir.config_parameter"].set_param(
            "auth_brute_force.whitelist_remotes",
            ",".join(whitelist),
        )
