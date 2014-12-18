# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class BaseConfigInheritModel(orm.AbstractModel):

    """
    Abstract model which can be inherited by model which need to have
        configuration field. This configuration can be inherited by children
        and specified models, and then be overridden by them.
    """

    _name = 'base.config.inherit.model'

    _base_config_inherit_model = False
    _base_config_inherit_key = False
    _base_config_inherit_o2m = False

    _columns = {
        'base_config_inherit_line_del_ids': fields.one2many(
            'base.config.inherit.line.del', 'res_id',
            domain=lambda self: [('model', '=', self._name)],
            auto_join=True,
            string='Configuration line deleted'
        ),
    }

    def _prepare_config(self, cr, uid, id, record, vals=None, context=None):
        """
        This function can be overridden by inheriting model
        to specify the field contains in the configuration
        """

        if vals is None:
            vals = {}

        return vals

    def _get_external_config(self, cr, uid, record, context=None):
        """
        This function can be overridden in inheriting model
        to specify how the configuration can be recovered from other models
        """
        return {}

    def _get_child_ids(self, cr, uid, ids, context=None):
        """
        This function can be overriden in inheriting model
        to specify how the children are found
        """
        return self.search(
            cr, uid,
            [('parent_id', 'in', ids)], context=context
        )

    def _update_stored_config_external_children(
            self, cr, uid, ids, context=None
    ):
        """
        This function can be overriden in inheriting model
        to trigger the compute of children models
        """
        return True

    def _purge_existing_configuration(self, cr, uid, ids, context=None):
        """
        Purge all computed configuration in the given record
        """
        config_obj = self.pool[self._base_config_inherit_model]
        config_del_obj = self.pool['base.config.inherit.line.del']

        # Purge all existing configuration
        config_stored_ids = config_obj.search(
            cr, uid,
            [
                ('model', '=', self._name), ('res_id', 'in', ids),
                ('stored', '=', True)
            ],
            context=context
        )
        config_obj.unlink(cr, uid, config_stored_ids, context=context)
        config_del_ids = config_del_obj.search(
            cr, uid,
            [('model', '=', self._name), ('res_id', 'in', ids)],
            context=context
        )
        config_del_obj.unlink(cr, uid, config_del_ids, context=context)

    def _get_parent_configuration(
            self, cr, uid, record, config_lines, config_line_dels, context=None
    ):

        config_obj = self.pool[self._base_config_inherit_model]
        config_del_obj = self.pool['base.config.inherit.line.del']

        # First, get the deleted lines from parent
        parent_config_del_ids = config_del_obj.search(
            cr, uid,
            [
                ('model', '=', self._name),
                ('res_id', '=', record.parent_id.id)
            ],
            context=context
        )
        for config_line_del in config_del_obj.browse(
                cr, uid, parent_config_del_ids, context=context
        ):
            config_line_dels[config_line_del['key']] = {
                'model': self._name,
                'res_id': record.id,
                'key': config_line_del['key']
            }
            if config_line_del['key'] in config_lines:
                del config_lines[config_line_del['key']]

        # Get parent config
        parent_config_ids = config_obj.search(
            cr, uid,
            [
                ('model', '=', self._name),
                ('res_id', '=', record.parent_id.id),
                ('stored', '=', True)
            ],
            context=context
        )
        for config_line in config_obj.browse(
            cr, uid, parent_config_ids, context=context
        ):
            key = getattr(
                config_line, self._base_config_inherit_key
            ).id
            config_lines[key] = self._prepare_config(
                cr, uid, record.id, config_line, context=context
            )

        return config_lines, config_line_dels

    def _update_stored_config(self, cr, uid, ids, context=None):
        """
        When called, this function will purge all stored configuration
        and recompute them, by recover it from parent and checking
        if the configuration isn't override in the current record.
        """

        config_obj = self.pool[self._base_config_inherit_model]
        config_del_obj = self.pool['base.config.inherit.line.del']

        self._purge_existing_configuration(cr, uid, ids, context=context)

        for record in self.browse(cr, uid, ids, context=context):

            config_lines = {}
            config_line_dels = {}

            # Get configuration from other model, if exist
            for key, config in self._get_external_config(
                cr, uid, record, context=context
            ).iteritems():
                config_lines[key] = config

            # Get configuration from parent, if exist
            if 'parent_id' in record and record.parent_id:

                config_lines, config_line_dels = \
                    self._get_parent_configuration(
                        cr, uid, record,
                        config_lines, config_line_dels, context=context
                    )

            # Modify the configuration for the current object
            for config_line in getattr(record, self._base_config_inherit_o2m):
                key = getattr(config_line, self._base_config_inherit_key).id
                if config_line.action == 'add':
                    config_lines[key] = self._prepare_config(
                        cr, uid, record.id, config_line,
                        vals=None, context=context
                    )
                    if key in config_line_dels:
                        del config_line_dels[key]
                elif config_line.action == 'remove':
                    config_line_dels[key] = {
                        'model': self._name, 'res_id': record.id, 'key': key
                    }
                    if key in config_lines:
                        del config_lines[key]

            config_lines_list = []
            for key, config_line in config_lines.iteritems():
                config_lines_list.append(config_line)

            sorted(config_lines_list, key=lambda config: (
                config['sequence'], config[self._base_config_inherit_key]
            ))

            # Create the computed configuration
            for config_line in config_lines_list:
                config_obj.create(cr, uid, config_line, context=context)

            for key, config_line_del in config_line_dels.iteritems():
                config_del_obj.create(
                    cr, uid, config_line_del, context=context
                )

        # Update children
        if 'parent_id' in self._columns:
            child_ids = self._get_child_ids(cr, uid, ids, context=context)
            if child_ids:
                self._update_stored_config(cr, uid, child_ids, context=context)

        # Update impacted models
        self._update_stored_config_external_children(
            cr, uid, ids, context=context
        )

    def create(self, cr, uid, vals, context=None):
        # When we create the record, we compute the configuration
        res = super(BaseConfigInheritModel, self).create(
            cr, uid, vals, context=context
        )
        self._update_stored_config(cr, uid, [res], context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # When we write in the record, we recompute the configuration
        res = super(BaseConfigInheritModel, self).write(
            cr, uid, ids, vals, context=context
        )
        self._update_stored_config(cr, uid, ids, context=context)
        return res


class BaseConfigInheritLine(orm.AbstractModel):

    """
    Lines containing the configuration. Depending of the stored field,
    it is either a line computed by the update function or a line
    which override the configuration
    """

    _name = 'base.config.inherit.line'

    _columns = {
        'model': fields.char('Related Document Model', size=128, select=1),
        'res_id': fields.integer('Related Document ID', select=1),
        'action': fields.selection([
            ('add', 'Add'), ('remove', 'Remove')
        ], 'Action', required=True),
        'sequence': fields.integer('Sequence'),
        'stored': fields.boolean('Stored?'),
    }

    _defaults = {
        'action': 'add'
    }

    _order = 'sequence'


class BaseConfigInheritLineDel(orm.Model):

    """
    Lines created when a configuration line where deleted in parent,
    used to remove the specified configuration fromchildren
    """

    _name = 'base.config.inherit.line.del'

    _columns = {
        'model': fields.char('Related Document Model', size=128, select=1),
        'res_id': fields.integer('Related Document ID', select=1),
        'key': fields.integer('Key')
    }
