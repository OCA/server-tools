# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from lxml import etree
from openerp import api, models, tools, _


class UnquoteObject(str):
    def __getattr__(self, name):
        return UnquoteObject('%s.%s' % (self, name))

    def __repr__(self):
        return self

    def __call__(self, *args, **kwargs):
        return UnquoteObject(
            '%s(%s)' % (
                self,
                ','.join(
                    [
                        UnquoteObject(
                            a if not isinstance(a, basestring)
                            else "'%s'" % a
                        )
                        for a in args
                    ] +
                    [
                        '%s=%s' % (UnquoteObject(k), v)
                        for (k, v) in kwargs.iteritems()
                    ]
                )
            )
        )


class UnquoteEvalObjectContext(tools.misc.UnquoteEvalContext):
    def __missing__(self, key):
        return UnquoteObject(key)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def apply_inheritance_specs(self, source, specs_tree, inherit_id):
        for specs, handled_by in self._iter_inheritance_specs(specs_tree):
            source = handled_by(source, specs, inherit_id)
        return source

    @api.model
    def _iter_inheritance_specs(self, spec):
        if spec.tag == 'data':
            for child in spec:
                for node, handler in self._iter_inheritance_specs(child):
                    yield node, handler
            return
        if spec.get('position') == 'attributes':
            for child in spec:
                node = etree.Element(spec.tag, **spec.attrib)
                node.insert(0, child)
                yield node, self._get_inheritance_handler_attributes(
                    child
                )
            return
        yield spec, self._get_inheritance_handler(spec)

    @api.model
    def _get_inheritance_handler(self, node):
        handler = super(IrUiView, self).apply_inheritance_specs
        if hasattr(
            self, 'inheritance_handler_%s' % node.tag
        ):
            handler = getattr(
                self,
                'inheritance_handler_%s' % node.tag
            )
        return handler

    @api.model
    def _get_inheritance_handler_attributes(self, node):
        handler = super(IrUiView, self).apply_inheritance_specs
        if hasattr(
            self, 'inheritance_handler_attributes_%s' % node.get('operation')
        ):
            handler = getattr(
                self,
                'inheritance_handler_attributes_%s' % node.get('operation')
            )
        return handler

    @api.model
    def inheritance_handler_attributes_python_dict(
        self, source, specs, inherit_id
    ):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="python_dict" key="$key">
                $keyvalue
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            python_dict = tools.safe_eval(
                node.get(attribute_node.get('name')) or '{}',
                UnquoteEvalObjectContext()
            )
            python_dict[attribute_node.get('key')] = UnquoteObject(
                attribute_node.text
            )
            node.attrib[attribute_node.get('name')] = str(python_dict)
        return source

    @api.model
    def inheritance_handler_xpath(self, source, specs, inherit_id):
        if not specs.get('position') == 'move':
            return super(IrUiView, self).apply_inheritance_specs(
                source, specs, inherit_id
            )
        node = self.locate_node(source, specs)
        target_node = self.locate_node(
            source, etree.Element(specs.tag, expr=specs.get('target'))
        )

        target_position = specs.get('target_position') or 'inside'

        if target_position == 'after':
            target_node.addnext(node)
        elif target_position == 'before':
            target_node.addprevious(node)
        elif target_position == 'inside':
            target_node.append(node)
        else:
            self.raise_view_error(
                _("Invalid target_position attribute: '%s'") % target_position,
                inherit_id,
                context=self.env.context
            )

        return source

    @api.model
    def inheritance_handler_attributes_list_add(
        self, source, specs, inherit_id
    ):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="list_add">
                $new_value
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get('name')
            old_value = node.get(attribute_name) or ''
            new_value = old_value + ',' + attribute_node.text
            node.attrib[attribute_name] = new_value
        return source

    @api.model
    def inheritance_handler_attributes_list_remove(
        self, source, specs, inherit_id
    ):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="list_remove">
                $value_to_remove
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get('name')
            old_values = (node.get(attribute_name) or '').split(',')
            remove_values = attribute_node.text.split(',')
            new_values = [x for x in old_values if x not in remove_values]
            node.attrib[attribute_name] = ','.join(filter(None, new_values))
        return source
