# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from hashlib import md5
import os.path
import json
import re
import base64
import unicodedata
try:
    from txlib.http.exceptions import NotFoundError, RequestError
except ImportError:
    NotFoundError = RequestError = None
try:
    import slugify as slugify_lib
except ImportError:
    slugify_lib = None
try:
    from github import UnknownObjectException
except ImportError:
    UnknownObjectException = None


class GithubProject(models.Model):
    _name = 'transbot.project'

    @api.one
    @api.depends('organization', 'project')
    def _get_name(self):
        self.name = "%s/%s" % (self.organization, self.project)

    organization = fields.Char(
        string="Organization", required=True,
        help="Name of the user/organization that owns the project")
    project = fields.Char(string="Project", required=True,
                          help="Name of the project to track")
    name = fields.Char(string="Full name", compute=_get_name)
    branches = fields.One2many(
        comodel_name='transbot.project.branch',
        inverse_name='project', string="Branches")
    logs = fields.One2many(
        comodel_name='transbot.log',
        inverse_name='project', string="Logs", readonly=True)

    @api.multi
    def get_branches(self):
        log_obj = self.env['transbot.log']
        branch_obj = self.env['transbot.project.branch']
        gh = self.env['transbot.config.settings'].get_github_connection()
        for project in self:
            log_obj.log_message(_("Updating project branches..."),
                                project=project.id)
            gh_organization = gh.get_organization(self.organization)
            gh_repo = gh_organization.get_repo(self.project)
            for gh_branch in gh_repo.get_branches():
                if not branch_obj.search([('project', '=', project.id),
                                          ('name', '=', gh_branch.name)]):
                    branch_obj.create({'project': project.id,
                                       'name': gh_branch.name})
                    log_obj.log_message(_("Created new branch '%s'" %
                                          gh_branch.name),
                                        project=project.id)

    def _look_translations(self, gh_commit, from_commit=False):
        """This method looks recursively for translations starting from a
        Github commit, and jumping to parent commit until there is no more
        or it reaches 'from_commit' commit. If there is any new translation
        file or if an existing one has been modified, files are added to a set
        of modified files. It ignores files inside '__unported__' dir.
        """
        trans_files = set()
        pot_files = set()
        if from_commit and from_commit.sha == gh_commit.sha:
            return pot_files, trans_files
        for gh_file in gh_commit.files:
            if '__unported__' in gh_file.filename:
                continue
            extension = os.path.splitext(gh_file.filename)[1]
            if extension == '.po':
                trans_files.add(gh_file.filename)
            elif extension == '.pot':
                pot_files.add(gh_file.filename)
        if not gh_commit.parents:
            return trans_files
        else:
            for parent_commit in gh_commit.parents:
                pot_res, trans_res = self._look_translations(
                    parent_commit, from_commit=from_commit)
                pot_files = pot_files.union(pot_res)
                trans_files = trans_files.union(trans_res)
            return pot_files, trans_files

    def _look_translations_full(self, gh_repo, gh_branch):
        """This method checks for translations files on the current full
        content of a branch.
        :param gh_repo: Github repository reference
        :param gh_branch: Github branch (belonging to the repository) reference
        :return:
        """
        trans_files = []
        pot_files = []
        gh_tree = gh_repo.get_git_tree(gh_branch.commit.sha, recursive=True)
        for element in gh_tree.tree:
            if '__unported__' in element.path:
                continue
            extension = os.path.splitext(element.path)[1]
            if extension == '.po':
                trans_files.append(element.path)
            elif extension == '.pot':
                pot_files.append(element.path)
        return pot_files, trans_files

    @api.multi
    def check_github_updates(self):
        if not self.ids:
            self = self.search([])
        log_obj = self.env['transbot.log']
        branch_obj = self.env['transbot.project.branch']
        transbot_settings = self.env['transbot.config.settings']
        gh = transbot_settings.get_github_connection()
        for project in self:
            log_obj.log_message(_("Checking for new content in Github..."),
                                project=project.id)
            gh_organization = gh.get_organization(self.organization)
            gh_repo = gh_organization.get_repo(self.project)
            # Get only active branches
            branches = branch_obj.search([('project', '=', project.id),
                                          ('active', '=', True)])
            for branch in branches:
                gh_branch = gh_repo.get_branch(branch.name)
                if branch.last_commit_sha:
                    pot_files, trans_files = self._look_translations(
                        gh_branch.commit,
                        gh_repo.get_commit(branch.last_commit_sha))
                else:
                    pot_files, trans_files = self._look_translations_full(
                        gh_repo, gh_branch)
                if pot_files:
                    self._upload_templates_transifex(
                        gh, gh_repo, gh_branch, branch, pot_files)
                if trans_files:
                    self._upload_translations_transifex(
                        gh, gh_repo, gh_branch, branch, trans_files)
                branch.last_commit_sha = gh_branch.commit.sha

    def _upload_templates_transifex(
            self, gh, gh_repo, gh_branch, branch, pot_files):
        transbot_settings = self.env['transbot.config.settings']
        params = transbot_settings.get_default_parameters()
        project_slug = self._get_or_create_transifex_project(
            gh_repo, gh_branch,
            organization=params['transifex_organization'],
            team=params['transifex_team'], branch=branch)
        for pot_file in pot_files:
            if pot_file.count('/') != 2:
                self.env['transbot.log'].log_message(
                    _("Incorrect depth in path for file %s" % pot_file),
                    log_type='error', project=branch.project.id)
                return
            try:
                gh_file = gh_repo.get_file_contents(pot_file,
                                                    ref=gh_branch.name)
            except UnknownObjectException:
                # This is a deleted file - Not do anything
                # Or should I delete it also on Transifex?
                continue
            self._add_or_replace_transifex_resource(
                project_slug, pot_file, base64.b64decode(gh_file.content),
                branch)

    def _upload_translations_transifex(
            self, gh, gh_repo, gh_branch, branch, trans_files):
        transbot_settings = self.env['transbot.config.settings']
        params = transbot_settings.get_default_parameters()
        project_slug = self._get_or_create_transifex_project(
            gh_repo, gh_branch,
            organization=params['transifex_organization'],
            team=params['transifex_team'], branch=branch)
        for trans_file in trans_files:
            if trans_file.count('/') != 2:
                self.env['transbot.log'].log_message(
                    _("Incorrect depth in path for file %s" % trans_file),
                    log_type='error', project=branch.project.id)
                return
            try:
                gh_file = gh_repo.get_file_contents(trans_file,
                                                    ref=gh_branch.name)
            except UnknownObjectException:
                # This is a deleted file - Not do anything
                # Or should I delete it also on Transifex?
                continue
            self._add_or_replace_transifex_translation(
                project_slug, trans_file,
                base64.b64decode(gh_file.content), branch)

    def get_project_slug(self, gh_repo, gh_branch):
        return self._get_slug("%s-%s" % (gh_repo.name, gh_branch.name))

    def _get_slug(self, name):
        if slugify_lib:
            # There are 2 different libraries only python-slugify is supported
            try:
                return slugify_lib.slugify(name)
            except TypeError:
                pass
        uni = unicodedata.normalize('NFKD',
                                    name).encode('ascii',
                                                 'ignore').decode('ascii')
        slug = re.sub('[\W_]', ' ', uni).strip().lower()
        slug = re.sub('[-\s]+', '-', slug)
        return slug

    def _get_hash_for_strings(self, strings):
        return md5(':'.join([x['translation'] for x in strings]).encode(
            'utf-8')).hexdigest()

    def _get_or_create_transifex_project(
            self, gh_repo, gh_branch, organization=None, team=None,
            branch=None):
        project_slug = self.get_project_slug(gh_repo, gh_branch)
        tx = self.env['transbot.config.settings'].get_transifex_connection()
        project = None
        try:
            project = tx.get('/api/2/project/%s' % project_slug)
        except NotFoundError:
            pass
        if not project:
            project = {
                'name': "%s (%s)" % (gh_repo.name, gh_branch.name),
                'slug': project_slug,
                'description': gh_repo.description or gh_repo.full_name,
                'source_language_code': 'en',
                'repository_url': gh_repo.html_url,
                'license': 'permissive_open_source',
                'auto_join': True,
                'fill_up_resources': True,
                'private': False,
            }
            if organization:
                project['organization'] = organization
            if team:
                project['team'] = team
            tx.post('/api/2/projects/', json.dumps(project))
            self.env['transbot.log'].log_message(
                _("New project '%s' created in Transifex." %
                  project_slug), project=branch.project.id)
        return project['slug']

    def _add_or_replace_transifex_resource(
            self, project_slug, file_path, file_contents, branch):
        """Adds or replace a Transifex resource inside a project with the
        given data.
        :param project_slug: Slug reference of Transifex project
        :param resource_name: name of the resource
        :param file_contents: contents of the template in the native language
        """
        tx = self.env['transbot.config.settings'].get_transifex_connection()
        resource_name = os.path.splitext(os.path.basename(file_path))[0]
        resource_slug = self._get_slug(resource_name)
        resource = False
        try:
            resource = tx.get('/api/2/project/%s/resource/%s' %
                              (project_slug, resource_slug))
        except NotFoundError:
            pass
        if not resource:
            resource = {
                'slug': resource_slug,
                'name': resource_name,
                'accept_translations': True,
                'i18n_type': 'PO',
                'priority': 0,
                'content': file_contents,
            }
            tx.post('/api/2/project/%s/resources' % project_slug,
                    json.dumps(resource))
            self.env['transbot.log'].log_message(
                _("New resource '%s' created for project '%s' in Transifex.") %
                (resource_name, project_slug), project=branch.project.id)
        else:
            resource = {'content': file_contents}
            tx.put('/api/2/project/%s/resource/%s/content' %
                   (project_slug, resource_slug), json.dumps(resource))
            self.env['transbot.log'].log_message(
                _("Updated resource '%s' for project '%s' in Transifex.") %
                (resource_name, project_slug), project=branch.project.id)

    def _add_or_replace_transifex_translation(
            self, project_slug, file_path, file_contents, branch):
        """Adds or replace a Transifex resource inside a project with the
        given data.
        :param project_slug: Slug reference of Transifex project
        :param file_path: complete path of the file (to extract resource and
          language code)
        :param file_contents: contents of the template in the native language
        :param project: Project reference for the log
        """
        tx = self.env['transbot.config.settings'].get_transifex_connection()
        resource_slug = self._get_slug(
            os.path.basename(os.path.dirname(os.path.dirname(file_path))))
        try:
            tx.get('/api/2/project/%s/resource/%s' % (project_slug,
                                                      resource_slug))
        except NotFoundError:
            self.env['transbot.log'].log_message(
                _("Template not found in Transifex for file %s" % file_path),
                log_type='error', project=branch.project.id)
            return
        lang_code = os.path.splitext(os.path.basename(file_path))[0]
        translation = {'content': file_contents}
        try:
            tx.put('/api/2/project/%s/resource/%s/translation/%s' %
                   (project_slug, resource_slug, lang_code),
                   json.dumps(translation))
            self.env['transbot.log'].log_message(
                _("Updated translation '%s' for resource '%s' of project '%s' "
                  "in Transifex.") % (lang_code, resource_slug, project_slug),
                project=branch.project.id)
            # Update cached hash for comparing new translations made on
            # Transifex
            strings = tx.get('/api/2/project/%s/resource/%s/translation/%s'
                             '/strings' % (project_slug, resource_slug,
                                           lang_code))
            h = self._get_hash_for_strings(strings)
            translation_obj = self.env['transbot.project.branch.translation']
            translation = translation_obj.search(
                [('resource', '=', resource_slug),
                 ('language', '=', lang_code),
                 ('branch', '=', branch.id)])
            if translation:
                translation.hash = h
            else:
                translation.create({'hash': h,
                                    'resource': resource_slug,
                                    'language': lang_code,
                                    'branch': branch.id})
        except RequestError as e:
            self.env['transbot.log'].log_message(
                _("Error updating translation '%s' for resource '%s' of "
                  "project '%s' in Transifex. Reason: %s") %
                (lang_code, resource_slug, project_slug, e),
                log_type='error', project=branch.project.id)

    @api.multi
    def check_transifex_updates(self):
        if not self.ids:
            self = self.search([])
        log_obj = self.env['transbot.log']
        branch_obj = self.env['transbot.project.branch']
        settings_obj = self.env['transbot.config.settings']
        translation_obj = self.env['transbot.project.branch.translation']
        gh = settings_obj.get_github_connection()
        tx = settings_obj.get_transifex_connection()
        for project in self:
            log_obj.log_message(
                _("Checking for new content in Transifex..."),
                project=project.id)
            gh_organization = gh.get_organization(self.organization)
            gh_repo = gh_organization.get_repo(self.project)
            # Get only active branches
            branches = branch_obj.search([('project', '=', project.id),
                                          ('active', '=', True)])
            for branch in branches:
                gh_branch = gh_repo.get_branch(branch.name)
                # Check resources in Transifex
                project_slug = self.get_project_slug(gh_repo, gh_branch)
                resources = tx.get('/api/2/project/%s/resources/' %
                                   project_slug)
                for resource in resources:
                    # Check if exists on Github (there's a module for it)
                    try:
                        gh_repo.get_dir_contents('/%s' % resource['slug'],
                                                 gh_branch.name)
                    except UnknownObjectException:
                        self.env['transbot.log'].log_message(
                            _("Resource %s in Transifex can't be located in "
                              "Github. Deleted module?"), log_type='error',
                            project=project.id)
                        continue
                    # Get translations
                    resource = tx.get(
                        '/api/2/project/%s/resource/%s?details' %
                        (project_slug, resource['slug']))
                    for lang in resource['available_languages']:
                        strings = tx.get(
                            '/api/2/project/%s/resource/%s/translation/%s/'
                            'strings' % (project_slug, resource['slug'],
                                         lang['code']))
                        if any([x['translation'] for x in strings]):
                            h = self._get_hash_for_strings(strings)
                            translation = translation_obj.search(
                                [('resource', '=', resource['slug']),
                                 ('language', '=', lang['code']),
                                 ('branch', '=', branch.id)])
                            if not translation or translation.hash != h:
                                self._add_or_replace_github_translation(
                                    gh_repo, gh_branch, project_slug,
                                    resource['slug'], lang['code'], project)
                                h = self._get_hash_for_strings(strings)
                                if translation:
                                    translation.hash = h
                                else:
                                    translation.create({
                                        'hash': h,
                                        'resource': resource['slug'],
                                        'language': lang['code'],
                                        'branch': branch.id})
                # Force an update of last commit of the branch
                branch.last_commit_sha = gh_branch.commit.sha

    def _add_or_replace_github_translation(
            self, gh_repo, gh_branch, project_slug, resource_slug, lang_code,
            project):
        tx = self.env['transbot.config.settings'].get_transifex_connection()
        # Get file
        po_file = tx.get('/api/2/project/%s/resource/%s/translation/%s' %
                         (project_slug, resource_slug, lang_code))
        # Check if file exists already in Github
        path = '/%s/i18n/%s.po' % (resource_slug, lang_code)
        try:
            # Check if file exists
            gh_file = gh_repo.get_contents(path, gh_branch.name)
            sha = gh_file.sha
        except UnknownObjectException:
            sha = None
        gh_repo.put_file_contents(
            path, "Transbot '%s' translation automatic update for '%s'" %
            (lang_code, resource_slug), po_file['content'], sha,
            gh_branch.name)
        self.env['transbot.log'].log_message(
            _("Language '%s' for module '%s' updated on Github.") %
            (lang_code, resource_slug), project=project.id)


class GithubProjectBranch(models.Model):
    _name = 'transbot.project.branch'

    name = fields.Char(string="Name", readonly=True, required=True)
    active = fields.Boolean(string="Active", default=True)
    project = fields.Many2one(comodel_name="transbot.project",
                              string="Project", readonly=True, required=True,
                              ondelete="cascade")
    last_commit_sha = fields.Char(string="Last commit SHA", readonly=True)


class GithubProjectBranchTranslation(models.Model):
    _name = 'transbot.project.branch.translation'

    language = fields.Char(string='Language')
    hash = fields.Char(string="Hash")
    resource = fields.Char(string="Resource")
    branch = fields.Many2one(comodel_name='transbot.project.branch',
                             string="Branch")
