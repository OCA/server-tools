# -*- encoding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
#    planned by: nhomar@vauxoo.com
#                moylop260@vauxoo.com
############################################################################

from pprint import pprint
import sys

from openerp import api, models


class Webhook(models.Model):
    _inherit = 'webhook'

    @api.one
    def set_driver_remote_address(self):
        super(Webhook, self).set_driver_remote_address()
        self.env.webhook_driver_address.update({
            'github': ['192.30.252.0/22']
        })

    @api.one
    def set_event(self):
        super(Webhook, self).set_event()
        if not self.env.webhook_event and \
                self.env.webhook_driver_name == 'github':
            self.env.webhook_event = \
                self.env.request.httprequest.headers.get(
                    'X-Github-Event')

    @api.one
    def run_webhook_github_pull_request(self):
        """
        sys.stdout.write("I'm here: run_webhook_github_pull_request\n")
        # pprint(self.env.request.jsonrequest)
        sys.stdout.write("PR change in: %s/%s/pull/%s\n" % (
            self.env.request.jsonrequest['repository']['owner']['login'],
            self.env.request.jsonrequest['repository']['name'],
            self.env.request.jsonrequest['pull_request']['number']
        ))
        """
        return True

    @api.one
    def run_webhook_github_push(self):
        """
        sys.stdout.write("I'm here: run_webhook_github_push\n")
        pprint(self.env.request.jsonrequest)
        sys.stdout.write("Push change in: %s/%s\n" % (
            self.env.request.jsonrequest['repository']['owner']['name'],
            self.env.request.jsonrequest['repository']['name']
        ))
        sys.stdout.write(
            "self.env.request.jsonrequest['ref']")
        sys.stdout.write(
            self.env.request.jsonrequest['ref'] + "\n")
        sys.stdout.write(
            "self.env.request.jsonrequest['base_ref']")
        sys.stdout.write(
            self.env.request.jsonrequest['base_ref'] + "\n")
        """
        return True

    @api.one
    def run_webhook_github_commit_comment(self):
        return True

    @api.one
    def run_webhook_github_create(self):
        return True

    @api.one
    def run_webhook_github_delete(self):
        return True

    @api.one
    def run_webhook_github_deployment(self):
        return True

    @api.one
    def run_webhook_github_deployment_status(self):
        return True

    @api.one
    def run_webhook_github_fork(self):
        return True

    @api.one
    def run_webhook_github_gollum(self):
        return True

    @api.one
    def run_webhook_github_issue_comment(self):
        return True

    @api.one
    def run_webhook_github_issues(self):
        return True

    @api.one
    def run_webhook_github_member(self):
        return True

    @api.one
    def run_webhook_github_membership(self):
        return True

    @api.one
    def run_webhook_github_page_build(self):
        return True

    @api.one
    def run_webhook_github_public(self):
        return True

    @api.one
    def run_webhook_github_pull_request_review_comment(self):
        return True

    @api.one
    def run_webhook_github_repository(self):
        return True

    @api.one
    def run_webhook_github_release(self):
        return True

    @api.one
    def run_webhook_github_status(self):
        return True

    @api.one
    def run_webhook_github_team_add(self):
        return True

    @api.one
    def run_webhook_github_watch(self):
        return True
