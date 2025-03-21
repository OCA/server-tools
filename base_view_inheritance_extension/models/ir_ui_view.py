# Copyright 2016 Therp BV <https://therp.nl>
# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# Copyright 2023 Tecnativa - Carlos Dauden
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import ast
import re

from lxml import etree

from odoo import api, models
from odoo.osv import expression


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
        if type(k1) is not type(k2):
            return False
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
        if hasattr(self, f"inheritance_handler_{node.tag}"):
            handler = getattr(self, f"inheritance_handler_{node.tag}")
        return handler

    @api.model
    def _get_inheritance_handler_attributes(self, node):
        handler = super().apply_inheritance_specs
        if hasattr(self, f"_inheritance_handler_attributes_{node.get('operation')}"):
            handler = getattr(
                self, f"_inheritance_handler_attributes_{node.get('operation')}"
            )
        return handler

    @api.model
    def _inheritance_handler_attributes_update(self, source, specs):
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
            node_attr = (node.get(attr_name) or "{}").strip()
            source_ast = ast.parse(node_attr, mode="eval").body
            update_ast = ast.parse(spec.text.strip(), mode="eval").body
            if not isinstance(source_ast, ast.Dict):
                raise TypeError(f"Attribute `{attr_name}` is not a dict")
            if not isinstance(update_ast, ast.Dict):
                raise TypeError(f"Operation for attribute `{attr_name}` is not a dict")
            # Update node ast dict
            source_ast = ast_dict_update(source_ast, update_ast)
            # Dump the ast back to source
            node.attrib[attr_name] = ast.unparse(source_ast).strip()
        return source

    @api.model
    def _inheritance_handler_attributes_text_add(self, source, specs):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="text_add">
                $text_before {old_value} $text_after
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get("name")
            old_value = node.get(attribute_name) or ""
            node.attrib[attribute_name] = attribute_node.text.format(
                old_value=old_value
            )
        return source

    @api.model
    def _inheritance_handler_attributes_domain_add(self, source, specs):
        """Implement
        <$node position="attributes">
            <attribute name="$attribute" operation="domain_add"
                       condition="$field_condition" join_operator="OR">
                $domain_to_add
            </attribute>
        </$node>"""
        node = self.locate_node(source, specs)
        for attribute_node in specs:
            attribute_name = attribute_node.get("name")
            condition = attribute_node.get("condition")
            join_operator = attribute_node.get("join_operator") or "AND"
            old_value = node.get(attribute_name) or ""
            if old_value:
                old_domain = ast.literal_eval(
                    self._var2str_domain_text(old_value.strip())
                )
                new_domain = ast.literal_eval(
                    self._var2str_domain_text(attribute_node.text.strip())
                )
                if join_operator == "OR":
                    new_value = str(expression.OR([old_domain, new_domain]))
                else:
                    new_value = str(expression.AND([old_domain, new_domain]))
                new_value = self._str2var_domain_text(new_value)
                old_value = "".join(old_value.splitlines())
            else:
                # We must ensure that the domain definition has not line breaks because
                # in update mode the domain cause an invalid syntax error
                new_value = attribute_node.text.strip()
            if condition:
                new_value = f"{condition} and {new_value} or {old_value or []}"
            node.attrib[attribute_name] = new_value
        return source

    @api.model
    def _var2str_domain_text(self, domain_str):
        """Replaces var names with str names to allow eval without defined vars"""
        # Replace fields in 2 steps because 1 step returns "parent_sufix"."var_sufix"
        regex_parent = re.compile(r"parent\.(\b\w+\b)")
        domain_str = re.sub(
            regex_parent, r"'parent.\1_is_a_var_to_replace'", domain_str
        )
        regex = re.compile(r"(?<!\')(\b\w+\b)(?!\')")
        return re.sub(regex, r"'\1_is_a_var_to_replace'", domain_str)

    @api.model
    def _str2var_domain_text(self, domain_str):
        """Revert var2str_domain_text cleaning apostrophes and suffix in vars"""
        pattern = re.compile(r"'(parent\.[^']+)_is_a_var_to_replace'")
        domain_str = pattern.sub(r"\1", domain_str)
        pattern = re.compile(r"'([^']+)_is_a_var_to_replace'")
        return pattern.sub(r"\1", domain_str)
