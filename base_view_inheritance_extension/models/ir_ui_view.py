# Copyright 2016 Therp BV <https://therp.nl>
# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import ast
import logging

try:
    import astor
except ImportError as err:  # pragma: no cover
    _logger = logging.getLogger(__name__)
    _logger.debug(err)

from lxml import etree

from odoo import api, models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def apply_inheritance_specs(self, source, specs_tree, pre_locate=lambda s: True):
        for specs, handled_by in self._iter_inheritance_specs(specs_tree):
            pre_locate(specs)
            source = handled_by(source, specs)
        return source

    @api.model
    def _iter_inheritance_specs(self, spec):
        if spec.tag == "data":
            for child in spec:
                for node, handler in self._iter_inheritance_specs(child):
                    yield node, handler
            return
        if spec.get("position") == "attributes":
            if all(not c.get("operation") for c in spec):
                yield spec, self._get_inheritance_handler(spec)
                return
            for child in spec:
                node = etree.Element(spec.tag, **spec.attrib)
                node.insert(0, child)
                yield node, self._get_inheritance_handler_attributes(child)
            return
        yield spec, self._get_inheritance_handler(spec)

    @api.model
    def _get_inheritance_handler(self, node):
        handler = super(IrUiView, self).apply_inheritance_specs
        if hasattr(self, "inheritance_handler_%s" % node.tag):
            handler = getattr(self, "inheritance_handler_%s" % node.tag)
        return handler

    @api.model
    def _get_inheritance_handler_attributes(self, node):
        handler = super(IrUiView, self).apply_inheritance_specs
        if hasattr(self, "inheritance_handler_attributes_%s" % node.get("operation")):
            handler = getattr(
                self, "inheritance_handler_attributes_%s" % node.get("operation")
            )
        return handler

    @api.model
    def inheritance_handler_attributes_python_dict(self, source, specs):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="python_dict" key="$key">
                $keyvalue
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attr_name = attribute_node.get("name")
            attr_key = attribute_node.get("key")
            str_dict = node.get(attr_name) or "{}"
            ast_dict = ast.parse(str_dict.strip(), mode="eval").body
            assert isinstance(ast_dict, ast.Dict), f"'{attr_name}' is not a dict"
            assert attr_key, "No key specified for 'python_dict' operation"
            # Find the ast dict key
            # python < 3.8 uses ast.Str; python >= 3.8 uses ast.Constant
            key_idx = next(
                (
                    i
                    for i, k in enumerate(ast_dict.keys)
                    if (isinstance(k, ast.Str) and k.s == attr_key)
                    or (isinstance(k, ast.Constant) and k.value == attr_key)
                ),
                None,
            )
            # Update or create the key
            value = ast.parse(attribute_node.text.strip(), mode="eval").body
            if key_idx:
                ast_dict.values[key_idx] = value
            else:
                ast_dict.keys.append(ast.Str(attr_key))
                ast_dict.values.append(value)
            # Dump the ast back to source
            # TODO: once odoo requires python >= 3.9; use `ast.unparse` instead
            node.attrib[attribute_node.get("name")] = astor.to_source(
                ast_dict, pretty_source=lambda s: "".join(s).strip()
            )
        return source

    @api.model
    def inheritance_handler_attributes_list_add(self, source, specs):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="list_add">
                $new_value
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get("name")
            old_value = node.get(attribute_name) or ""
            new_value = old_value + "," + attribute_node.text
            node.attrib[attribute_name] = new_value
        return source

    @api.model
    def inheritance_handler_attributes_list_remove(self, source, specs):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="list_remove">
                $value_to_remove
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get("name")
            old_values = (node.get(attribute_name) or "").split(",")
            remove_values = attribute_node.text.split(",")
            new_values = [x for x in old_values if x not in remove_values]
            node.attrib[attribute_name] = ",".join([_f for _f in new_values if _f])
        return source
