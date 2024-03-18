# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo import api, fields, models
from odoo.tools.cache import ormcache


class View(models.Model):
    _inherit = "ir.ui.view"

    full_arch = fields.Text(
        compute="_compute_full_arch",
        compute_sudo=True,
        recursive=True,
        store=False,  # Cannot be stored: depends on non-stored fields,
        help="Technical field to check the fully combined architecture of the view:\n"
        "* for primary views, displays the full arch of the view, combined with the"
        " inheriting views' modifications\n"
        "* for extension views, inherits the full arch from the inherited view\n",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any({"inherit_id", "mode"}.intersection(v) for v in vals_list):
            type(self)._traverse_inherit_id.clear_cache(self.browse())
        return super().create(vals_list)

    def write(self, vals):
        if {"inherit_id", "mode"}.intersection(vals):
            type(self)._traverse_inherit_id.clear_cache(self.browse())
        return super().write(vals)

    def unlink(self):
        type(self)._traverse_inherit_id.clear_cache(self.browse())
        return super().unlink()

    @api.model
    def _get_full_arch_dependencies(self) -> list:
        # Hook method, can be overridden
        return [
            "active",
            "arch",
            "inherit_children_ids",
            "inherit_children_ids.full_arch",
            "inherit_id",
            "inherit_id.full_arch",
            "mode",
            "xml_id",
        ]

    @api.depends(lambda self: self._get_full_arch_dependencies())
    def _compute_full_arch(self):
        for view in self:
            # Update context's lang view-by-view to allow choosing different languages
            # for different views in inheriting modules if necessary
            view = view.with_context(lang=view._get_lang_for_full_arch())
            ancestor = view._get_ancestor()
            if view == ancestor:
                arch = view._get_formatted_arch()
                root_xml_id = view._get_root().xml_id
                if root_xml_id:
                    comment = etree.Comment(f"Defined in '{root_xml_id}'")
                    arch = "\n".join((etree.tostring(comment, encoding=str), arch))
                view.full_arch = arch
            else:
                view.full_arch = ancestor.full_arch

    def _get_lang_for_full_arch(self):
        # Hook method, can be overridden
        # ``full_arch`` should be, by default, compiled without translations to avoid
        # confusion in having different strings between the combined arch and the
        # original ones
        return None

    def _get_ancestor(self):
        return self.browse(self._traverse_inherit_id(stop_at_primary_view=True))

    def _get_root(self):
        return self.browse(self._traverse_inherit_id(stop_at_primary_view=False))

    @ormcache("self.id", "stop_at_primary_view")
    def _traverse_inherit_id(self, stop_at_primary_view=True):
        """Retrieves the view's furthermost inherit_id

        :param stop_at_primary_view: if True, traversal will stop as soon as a primary
            view (ie: ``mode == "primary"``) is found; if False, traversal will go on
            until the root view (ie: ``inherit_id == False``) is reached.
        :type stop_at_primary_view: bool
        :return: An ``ir.ui.view`` record's ID
        :rtype: int
        """
        if not self.inherit_id or (stop_at_primary_view and self.mode == "primary"):
            return self.id
        return self.inherit_id._traverse_inherit_id(stop_at_primary_view)

    def _get_formatted_arch(self):
        # Hook method, can be overridden
        self.ensure_one()
        method = self._get_format_arch_method()
        args = self._get_format_arch_args()
        kwargs = self._get_format_arch_kwargs()
        return method(*args, **kwargs)

    def _get_format_arch_method(self) -> callable:
        # Hook method, can be overridden
        self.ensure_one()
        return self.__default_format_arch

    # flake8: noqa: C901
    @staticmethod
    def __default_format_arch(doc, space: str = "  ", level: int = 0):
        """Default method for formatting the view's arch

        This default method is provided to avoid depending on specific packages or
        libraries.

        If another formatting method is preferred, please override method
        ``_get_format_arch_method()`` to return it, and (if needed) override methods
        ``_get_format_arch_args()`` and ``_get_format_arch_kwargs()`` accordingly.
        """

        def _get_levels(nd, lvl: int = 0, lvls=None) -> dict:
            """Returns a {node: level} dict, generated recursively with subnodes"""
            lvls = dict(lvls or [])
            lvls[nd] = lvl + len(tuple(nd.iterancestors()))
            for subnd in nd:
                lvls.update(_get_levels(subnd, lvl, lvls))
            return lvls

        def _adjust_text(nd, spc, lvl):
            old_text = nd.text
            if old_text is None:
                new_text = None
            else:
                is_multi_line = "\n" in old_text
                has_text = old_text.strip()
                is_comment = isinstance(nd, etree._Comment)
                if is_multi_line and has_text:
                    # Multi line with text (add suffix for comments)
                    orig_lines = old_text.split("\n")
                    lines = [" ".join(ln.split()) for ln in orig_lines if ln.strip()]
                    prefix = "\n" + (spc * (lvl + 1))
                    new_text = "".join(map(lambda x: prefix + x, lines))
                    if is_comment:
                        new_text += "\n" + (spc * lvl)
                elif is_multi_line:
                    # Multi line with no text
                    new_text = "\n\n" + (spc * lvl)
                elif has_text:
                    # Single line with text (add whitespaces for comments)
                    new_text = " ".join(old_text.split())
                    if new_text and isinstance(nd, etree._Comment):
                        new_text = " %s " % new_text
                else:
                    # Single line with no text
                    new_text = ""
            # Add extra space to text if we're expecting sub nodes
            if len(nd):
                new_text = (new_text or "").rstrip() + "\n" + (spc * (lvl + 1))
            nd.text = new_text

        def _adjust_tail(nd, spc, lvl):
            if not len(tuple(nd.iterancestors())):
                # Root tags do not accept tails
                new_tail = None
            else:
                old_tail = nd.tail
                has_tail = (old_tail or "").strip()
                if has_tail and old_tail.lstrip(" ").startswith("\n"):
                    # Multi line tail
                    orig_lines = old_tail.split("\n")
                    lines = [" ".join(ln.split()) for ln in orig_lines if ln.strip()]
                    prefix = "\n" + spc * lvl
                    new_tail = "".join(map(lambda x: prefix + x, lines))
                elif has_tail:
                    # Single line tail
                    new_tail = " ".join(old_tail.split())
                else:
                    # No real text in tail
                    new_tail = ""
                # Add spacing as suffix
                new_tail += "\n" + spc * lvl
            nd.tail = new_tail
            # Update last child's tail to match indentation
            if len(nd):
                last_child = tuple(nd.iterchildren())[-1]
                last_child.tail = (last_child.tail or "").rstrip() + "\n" + spc * lvl

        levels = _get_levels(doc, level).items()
        for node, level in sorted(levels, key=lambda x: x[1], reverse=True):
            _adjust_text(node, space, level)
            _adjust_tail(node, space, level)

        return etree.tostring(doc, pretty_print=True, encoding=str)

    def _get_format_arch_args(self) -> tuple:
        # Hook method, can be overridden
        self.ensure_one()
        return (etree.fromstring(self.read_combined()["arch"]),)

    def _get_format_arch_kwargs(self) -> dict:
        # Hook method, can be overridden
        self.ensure_one()
        return dict(space="  ", level=0)
