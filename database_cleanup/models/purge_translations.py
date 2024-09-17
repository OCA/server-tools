# Copyright 2021 Dimitrios Tanis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError


TRANSLATION_TYPE = [
    ('model', 'Model Field'),
    ('model_terms', 'Structured Model Field'),
    ('selection', 'Selection'),
    ('code', 'Code'),
    ('constraint', 'Constraint'),
    ('sql_constraint', 'SQL Constraint')
]


class CleanupPurgeLineTranslation(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.translation'
    _description = 'Purge Translation Lines'

    @api.model
    def _get_languages(self):
        langs = self.env['res.lang'].search([('translatable', '=', True)])
        return [(lang.code, lang.name) for lang in langs]

    translation_id = fields.Many2one(
        'ir.translation',
        'Translation',
        required=True,
        ondelete='CASCADE'
        )
    
    res_id = fields.Integer(string='Record ID', related='translation_id.res_id')
    lang = fields.Selection(selection='_get_languages', string='Language', related='translation_id.lang')
    type = fields.Selection(TRANSLATION_TYPE, string='Type', related='translation_id.type')
    value = fields.Text(string='Translation Value', related='translation_id.value')
    module = fields.Char(related='translation_id.module')
    state = fields.Selection([('to_translate', 'To Translate'),
                              ('inprogress', 'Translation in Progress'),
                              ('translated', 'Translated')],
                             string="Status", related='translation_id.state')

    reason = fields.Char()
    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.translation',
        'Purge Wizard',
        readonly=True
        )

    @api.multi
    def purge(self):
        rec = self.mapped('translation_id')
        rec.unlink()


class CleanupPurgeWizardTranslation(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.translation'
    _description = 'Purge Translations'

    @api.model
    def find(self):
        """
        Search for translations that are not used.
        """
        res = []
        ids_to_remove = set()
        parameters = {}

        # Find translations records that are not valid
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
            lang IS NULL
            OR "name" IS NULL
            OR res_id IS NULL
            OR "type" IS NULL;
            '''
        self.env.cr.execute(query)
        null_type = self.env.cr.fetchall()
        for rec in null_type:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Missing data'}))


        # Find translations that don't have src and value
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
            src IS NULL 
            AND value IS NULL
            '''
        if len(ids_to_remove) > 0:
            query += ' AND id NOT IN %(ids_to_remove)s'
            parameters = {
                'ids_to_remove': tuple(ids_to_remove),
            }
        self.env.cr.execute(query, parameters)
        parameters = {}
        missing_src_value = self.env.cr.fetchall()
        for rec in missing_src_value:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Missing Source and Value'}))


        # Find translations for uninstalled / deleted modules
        
        # TODO deleted module IS NULL and name = 'ir.model.fields,field_description' ????
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
            module IS NOT NULL 
            AND value IS NULL
            '''
        if len(ids_to_remove) > 0:
            query += ' AND id NOT IN %(ids_to_remove)s'
            parameters = {
                'ids_to_remove': tuple(ids_to_remove),
            }
        self.env.cr.execute(query, parameters)
        parameters = {}
        missing_src_value = self.env.cr.fetchall()
        for rec in missing_src_value:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Installed module but no translation'}))


        # Find translations for obsolete fields and selection values
        fields_list = []
        selection_fields_list = []
        fields = self.env['ir.model.fields'].search([])
#             for model in models:
        for fld in fields:
            name = "%s,%s" % (fld.model, fld.name)
            fields_list.append(name)
            if fld.ttype == 'selection':
                selection_fields_list.append(name)
        
        # Search and add obsolete fields
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
        "type" = 'model'
        AND name NOT IN %(name)s
        '''
        if len(ids_to_remove) > 0:
            query += ' AND id NOT IN %(ids_to_remove)s'
            parameters = {
                'ids_to_remove': tuple(ids_to_remove),
            }
        parameters['name'] = tuple(fields_list)
        self.env.cr.execute(query, parameters)
        parameters = {}
        deprecated_fld = self.env.cr.fetchall()
        for rec in deprecated_fld:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Deprecated / missing field'}))

        # Now search and add obsolete selection values
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
        "type" = 'selection'
        AND name NOT IN %(name)s
        '''
        if len(ids_to_remove) > 0:
            query += ' AND id NOT IN %(ids_to_remove)s'
            parameters = {
                'ids_to_remove': tuple(ids_to_remove),
            }
        parameters['name'] = tuple(selection_fields_list)
        self.env.cr.execute(query, parameters)
        parameters = {}
        deprecated_fld = self.env.cr.fetchall()
        for rec in deprecated_fld:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Deprecated selection for field'}))


        # Find translations for obsolete views (model_terms for ir.ui.view)
        # TODO add other name (like theme.ir.ui.view,arch, website.page,arch_db)
        views_list = []
        views = self.env['ir.ui.view'].search([])
        query = '''SELECT id, src, "name" FROM ir_translation it WHERE
        "type" = 'model_terms'
        AND name = 'ir.ui.view,arch_db'
        AND res_id NOT IN %(ids)s
        '''
        if len(ids_to_remove) > 0:
            query += ' AND id NOT IN %(ids_to_remove)s'
            parameters = {
                'ids_to_remove': tuple(ids_to_remove),
            }
        parameters['ids'] = tuple(views._ids)
        self.env.cr.execute(query, parameters)
        parameters = {}
        non_existing_views = self.env.cr.fetchall()
        for rec in non_existing_views:
            ids_to_remove.add(rec[0])
            res.append((0, 0, {
                'name': rec[1],
                'translation_id': rec[0],
                'reason': 'Obsolete / not existing view'}))


        if not res:
            raise UserError(_('No orphaned translations found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.translation', 'wizard_id', 'Translations to purge')
