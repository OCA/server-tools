# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests
import json
import re
from odoo.exceptions import UserError, ValidationError


class IrModule(models.Model):
    _inherit = "ir.module.module"

    mig_info_ids = fields.One2many("ir.module.migration.info", "module_id", string="Migration Info")

    def action_update_selected_module_info(self, record):
        repo_lst = self.check_module_link(record)

        module_list = []
        for rec in record:
            module_list.append(rec.name)
        for r_name in repo_lst:
            github_repo = self.get_github_repo(r_name)

            self.create_migration_record(github_repo, module_list)

    def create_migration_record(self, github_repo, odoo_modules):
        for repo in github_repo:
            for module_name in repo:
                if module_name in odoo_modules:
                    ir_module_module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
                    if ir_module_module:
                        for module_version in repo[module_name]:
                            ir_module_migration_info = self.env['ir.module.migration.info'].search(['&', ('mig_version', '=', module_version),
                                                                         ('module_id', '=', ir_module_module.id)],
                                                                        limit=1)
                            if ir_module_migration_info:
                                ir_module_migration_info.update({
                                    'module_name': module_name,
                                    'mig_version': module_version,
                                    'mig_title': repo[module_name][module_version].get('mig_title', ""),
                                    'mig_url': repo[module_name][module_version].get('mig_url', ""),
                                    'mig_status': repo[module_name][module_version].get('mig_state', ""),
                                    'mig_opened': repo[module_name][module_version].get('mig_opened', ""),
                                    'mig_merged': repo[module_name][module_version].get('mig_merged', ""),
                                    'mig_no_of_reviewers': repo[module_name][module_version].get('mig_no_of_reviewers',
                                                                                                 ""),
                                    'mig_no_of_comments': repo[module_name][module_version].get('mig_no_of_comments',
                                                                                                ""),
                                })
                            else:
                                self.env['ir.module.migration.info'].create({
                                    'module_name': module_name,
                                    'mig_version': module_version,
                                    'mig_title': repo[module_name][module_version].get('mig_title', ""),
                                    'mig_url': repo[module_name][module_version].get('mig_url', ""),
                                    'mig_status': repo[module_name][module_version].get('mig_state', ""),
                                    'mig_opened': repo[module_name][module_version].get('mig_opened', ""),
                                    'mig_merged': repo[module_name][module_version].get('mig_merged', ""),
                                    'mig_no_of_reviewers': repo[module_name][module_version].get('mig_no_of_reviewers',
                                                                                                 ""),
                                    'mig_no_of_comments': repo[module_name][module_version].get('mig_no_of_comments',
                                                                                                ""),
                                    'module_id': ir_module_module.id,
                                })

    def get_github_repo(self, reponame):

        # define the pull requests query by checking weather the next page existed or not
        # since graphql returns only 100 result at a time, then get the next query based on its cursor
        # loop until the next page doesn't exist
        getPage = True
        cursor = ""
        i = 1
        extracted_result = []
        while getPage:
            print("--------------------------------------------------")
            print("GETTING FOR PAGINATION ... " + str(i))
            print("")
            # "openupgrade"
            query = (
                    'query{'
                    'repository(owner: "OCA", name: "%s") {'
                    'pullRequests(first: 100 ' + cursor + ', orderBy: {field: CREATED_AT, direction: DESC}) {'
                                                          'totalCount '
                                                          'pageInfo { hasNextPage endCursor }'
                                                          'nodes {'
                                                          'title url state createdAt mergedAt number '
                                                          'author { login }'
                                                          'reviews { totalCount }'
                                                          'comments { totalCount }'
                                                          '}'
                                                          '}'
                                                          '}'
                                                          '}'
            ) % reponame

            # get the result in dictionary format
            result = self.run_query(query)

            migration_info = self.get_migration_info(result)

            # append the pagination result to list
            extracted_result.append(migration_info)

            getPage = result["data"]["repository"]["pullRequests"]["pageInfo"]["hasNextPage"]
            cursor = 'after:\"' + result["data"]["repository"]["pullRequests"]["pageInfo"]["endCursor"] + '\"'
            i = i + 1
        return extracted_result

    # define the method to make query call to graphql api
    def run_query(self, query):
        oca_token = self.env['ir.config_parameter'].sudo().get_param('oca_token', False)
        oca_username = self.env['ir.config_parameter'].sudo().get_param('oca_username', False)
        if not oca_token:
            raise UserError(_('Add Token in ir.config_parameter!'))

        # define headers
        headers = {"Authorization": "bearer " + oca_token}

        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

    def check_module_link(self, module_rec):
        repo_set = set()
        for rec in module_rec:
            if "github.com" in rec.website:
                repo_name = rec.website.split('/')[4]
            else:
                repo_name = "openupgrade"
            repo_set.add(repo_name)
        return list(repo_set)

    def get_migration_info(self, pull_requests):
        migration_info = dict()
        nodes = pull_requests["data"]["repository"]["pullRequests"]["nodes"]
        module_pr_id = 0
        for pr in nodes:
            title = pr["title"]
            if "MIG" in title:
                try:
                    if "] " in title:
                        module = title.split(":")[0].split("] ")[1]
                        vers = title.split(":")[0].split("] ")[0]
                        version = re.findall(r'\d+', vers)[0]
                    elif "0]" in title:
                        module = title.split(":")[0].split("0]")[1]
                        vers = title.split(":")[0].split("0] ")[0]
                        version = re.findall(r'\d+', vers)[0]
                    else:
                        module = ""
                        version = ""
                        # print("ignoring PR: " + title)
                        # print("     because title is not a good format to parse")
                        # print("")
                except Exception as e:
                    version = ""
                    # print("Error occured while parsing module name: ", e)
                    # print("")

                try:
                    # Look for pull requests of this module.
                    if module != "":
                        if re.search("([^\[MIG\]\[15\.0\]]|[^\[MIG\]\[15\.0\]])\s*{}\s*:.*$".format(module), title):
                            if pr["state"] in ("OPEN", "MERGED"):
                                # If multiple PRs are found, select the PR with the lowest ID number.
                                if not module_pr_id or module_pr_id > pr["number"]:
                                    module_pr_id = pr["number"]
                                    res = dict()
                                    res[version] = {
                                        "mig_title": pr["title"],
                                        "mig_url": pr["url"],
                                        "mig_state": pr["state"],
                                        "mig_opened": pr["createdAt"],
                                        "mig_merged": pr["mergedAt"],
                                        "mig_no_of_reviewers": pr["reviews"]["totalCount"],
                                        "mig_no_of_comments": pr["comments"]["totalCount"]
                                        # "mig_last_commented": date(2022, 6, 16),
                                    }
                                    migration_info[module] = res
                except Exception as e:
                    # print("Error Occured: ", e)
                    print("")

        return migration_info