import base64
import re
from tempfile import NamedTemporaryFile
from typing import Any
from xmlrpc.client import Boolean

import graphviz

from odoo import fields, models

FieldGraph = dict[fields.Field, Any]


class GraphError(Exception):
    pass


class ModelRelWizard(models.TransientModel):
    _name = "model_rel_wizard"
    _description = "Model Relationship Wizard"

    source_model = fields.Many2one(
        comodel_name="ir.model",
        required=True,
    )
    target_model = fields.Many2one(
        comodel_name="ir.model",
        required=True,
    )
    ignore_models = fields.Many2many(
        comodel_name="ir.model",
    )
    image = fields.Binary(
        string="Graph",
        readonly=True,
    )
    mermaid = fields.Text(
        default="",
        readonly=True,
    )
    white_list_regex = fields.Char()
    black_list_regex = fields.Char()

    def get_rel(self):
        self.ensure_one()
        self.mermaid = ""
        source_model = self._get_model_from_name(self.source_model.model)
        target_model = self._get_model_from_name(self.target_model.model)
        rel = self._get_rel(
            source_model,
            target_model,
            ignored_models=set(self.ignore_models),
            end_road_models=set(),
            used_models=set(),
            reach_target_models=set(),
            white_list_regex=(self.white_list_regex or "")
            .replace(".", r".")
            .replace("*", ".*"),
            black_list_regex=(self.black_list_regex or "")
            .replace(".", r".")
            .replace("*", ".*"),
        )
        rel_image = self._plot(rel)
        self.image = base64.encodebytes(rel_image)
        return {
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "view_mode": "form",
            "view_type": "form",
            "res_model": self._name,
            "target": "new",
        }

    def _plot(self, rel: FieldGraph) -> bytes:
        if not rel:
            return b""

        def _get_models(rel: FieldGraph) -> set[models.Model]:
            used_models = set()
            if rel is True:
                return set()
            for field in rel.keys():
                model = self._get_model_from_name(field.relation)
                used_models.add(model)
            return used_models

        def _plot_rel(rel: FieldGraph, dot: graphviz.Digraph) -> None:
            for field, sub_fields in rel.items():
                source = field.model_id.model
                target = field.relation
                attrs = {
                    "label": field.name,
                }
                if field.ttype == "many2many":
                    attrs["dir"] = "both"
                elif field.ttype == "many2one":
                    attrs["color"] = "red"
                dot.edge(source, target, **attrs)
                if sub_fields is not True:
                    _plot_rel(sub_fields, dot)

        all_models = _get_models(rel)
        all_models.add(self.source_model)
        all_models.add(self.target_model)
        dot = graphviz.Digraph(format="png")
        for model in all_models:
            attrs = {}
            if model == self.source_model:
                attrs["shape"] = "house"
            elif model == self.target_model:
                attrs["shape"] = "invhouse"
            dot.node(model.model, **attrs)
        _plot_rel(rel, dot)
        with NamedTemporaryFile(mode="w+b") as temp_file:
            dot.render(temp_file.name, format="png")
            with open(f"{temp_file.name}.png", "rb") as f:
                content = f.read()

        # os.remove(f"{temp_file.name}.png")

        return content

    def _get_rel_fields(self, model: models.Model) -> list[fields.Field]:
        def _is_field_relational(field: fields.Field) -> bool:
            return field.ttype in ["many2one", "one2many", "many2many"]

        def _not_ignored(field: fields.Field) -> bool:
            return field.name not in ("create_uid", "write_uid")

        return model.field_id.filtered(_is_field_relational).filtered(_not_ignored)

    def _get_model_from_name(self, name: str) -> models.Model:
        return self.env["ir.model"].search([("model", "=", name)], limit=1)

    def _get_rel(
        self,
        source_model: models.Model,
        target_model: models.Model,
        used_models: set[models.Model],
        ignored_models: set[models.Model],
        end_road_models: set[models.Model],
        reach_target_models: set[models.Model],
        white_list_regex: str = "",
        black_list_regex: str = "",
    ) -> FieldGraph | Boolean:
        is_start_or_end = source_model in (
            self._get_model_from_name(self.source_model.model),
            self._get_model_from_name(self.target_model.model),
        )
        if not is_start_or_end and white_list_regex:
            parts = white_list_regex.split(",")
            if not any(re.fullmatch(part, source_model.model) for part in parts):
                return False
        if not is_start_or_end and black_list_regex:
            parts = black_list_regex.split(",")
            if any(re.match(part, source_model.model) for part in parts):
                return False
        if source_model in ignored_models or source_model in end_road_models:
            return False
        if source_model in used_models:
            return False
        if source_model in reach_target_models or source_model == target_model:
            for model in used_models:
                reach_target_models.add(model)
            return True

        current_rels: FieldGraph = {}

        relational_fields = self._get_rel_fields(source_model)
        end_road = True
        for field in relational_fields:
            model = self._get_model_from_name(field.relation)
            rel = self._get_rel(
                model,
                target_model,
                used_models | {source_model},
                ignored_models,
                end_road_models,
                reach_target_models,
                white_list_regex,
                black_list_regex,
            )
            if rel is None:
                continue

            if rel:
                x2o = "||"
                x2m = "o{"
                m2x = "}o"
                direction = x2o if field.ttype == "many2one" else x2m
                self.mermaid += f'"{field.model_id.model}" {m2x}--{direction} "{field.relation}" : {field.name} \n'
                current_rels[field] = rel
            end_road = False
        if end_road:
            end_road_models.add(source_model)
        return current_rels
