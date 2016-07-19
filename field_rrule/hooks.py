# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import socket
import inspect


def post_load_hook():
    """do some trickery to have demo data/model on runbot, but nowhere else"""
    if socket.getfqdn().endswith('odoo-community.org'):  # pragma: nocover
        from . import demo  # flake8: noqa
        for frame, filename, lineno, funcname, line, index in inspect.stack():
            if 'package' in frame.f_locals:
                frame.f_locals['package'].info['demo'] =\
                    frame.f_locals['package'].info['demo_deactivated']
                break
