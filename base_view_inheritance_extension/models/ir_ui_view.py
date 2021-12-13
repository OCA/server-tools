# Copyright 2016 Therp BV <https://therp.nl>
# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

import astor
from lxml import etree

from odoo import api, models


def ast_dict_update(source, update):
    """Perform a dict `update` on an ast.Dict

    Behaves similar to :meth:`dict.update`, but on ast.Dict instead.
    Only compares string-like ast.Dict keys (ast.Str or ast.Constant).

    :returns: The updated ast.Dict
    :rtype: ast.Dict
    """
    if not isinstance(source, ast.Dict):
        raise TypeError("`source` must be an AST dict")
    if not isinstance(update, ast.Dict):
        raise TypeError("`update` must be an AST dict")

    def ast_key_eq(k1, k2):
        # python < 3.8 uses ast.Str; python >= 3.8 uses ast.Constant
        if type(k1) != type(k2):
            return False
        elif isinstance(k1, ast.Str):
            return k1.s == k2.s
        elif isinstance(k1, ast.Constant):
            return k1.value == k2.value

    toadd_uidx = []
    for uidx, ukey in enumerate(update.keys):
        found = False
        for sidx, skey in enumerate(source.keys):
            if ast_key_eq(ukey, skey):
                source.values[sidx] = update.values[uidx]
                found = True
                break
        if not found:
            toadd_uidx.append(uidx)
    for uidx in toadd_uidx:
        source.keys.append(update.keys[uidx])
        source.values.append(update.values[uidx])
    return source


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
        handler = super().apply_inheritance_specs
        if hasattr(self, "inheritance_handler_%s" % node.tag):
            handler = getattr(self, "inheritance_handler_%s" % node.tag)
        return handler

    @api.model
    def _get_inheritance_handler_attributes(self, node):
        handler = super().apply_inheritance_specs
        if hasattr(self, "inheritance_handler_attributes_%s" % node.get("operation")):
            handler = getattr(
                self, "inheritance_handler_attributes_%s" % node.get("operation")
            )
        return handler

    @api.model
    def inheritance_handler_attributes_update(self, source, specs):
        """Implement dict `update` operation on the attribute node.

        .. code-block:: xml

            <field position="attributes">
                <attribute name="context" operation="update">
                    {
                        "key": "value",
                    }
                </attribute>
            </field>
        """
        node = self.locate_node(source, specs)
        for spec in specs:
            attr_name = spec.get("name")
            # Parse ast from both node and spec
            source_ast = ast.parse(node.get(attr_name) or "{}", mode="eval").body
            update_ast = ast.parse(spec.text.strip(), mode="eval").body
            if not isinstance(source_ast, ast.Dict):
                raise TypeError(f"Attribute `{attr_name}` is not a dict")
            if not isinstance(update_ast, ast.Dict):
                raise TypeError(f"Operation for attribute `{attr_name}` is not a dict")
            # Update node ast dict
            source_ast = ast_dict_update(source_ast, update_ast)
            # Dump the ast back to source
            # TODO: once odoo requires python >= 3.9; use `ast.unparse` instead
            node.attrib[attr_name] = astor.to_source(
                source_ast,
                pretty_source=lambda s: "".join(s).strip(),
            )
        return source
