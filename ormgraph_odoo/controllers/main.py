# --------------------------------------------------------------------------
# ORMGraph for Odoo — Live Architecture & ERD Studio
# Author: Piyush Kumar (iam-piyush)
# Website: https://iampiyush.one
# Description: Interactive ORM architecture intelligence, visual ERDs, and
#              relational dependency pathfinding for Odoo models.
# License: LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
# --------------------------------------------------------------------------

import json
import logging
from collections import deque
from pathlib import Path

from odoo import http
from odoo.http import Response, request

_logger = logging.getLogger(__name__)


class ORMGraphController(http.Controller):
    @http.route(
        ["/ormgraph/studio", "/ormgraph/studio/<path:path>"],
        type="http",
        auth="user",
        methods=["GET"],
    )
    def studio_view(self, **kwargs):
        static_dir = Path(__file__).parent.parent / "static" / "src"
        index_file = static_dir / "index.html"

        if not index_file.exists():
            return Response(
                "ORMGraph Studio assets not found. Please verify static/src installation.",
                status=404,
            )

        content = index_file.read_text(encoding="utf-8")
        return Response(content, content_type="text/html;charset=utf-8")

    @http.route(["/_next/<path:path>"], type="http", auth="public", methods=["GET"], cors="*")
    def serve_next_static(self, path, **kwargs):
        file_path = Path(__file__).parent.parent / "static" / "src" / "_next" / path
        if not file_path.exists() or not file_path.is_file():
            return Response("Not found", status=404)

        content = file_path.read_bytes()
        content_type = "application/octet-stream"
        if path.endswith(".js"):
            content_type = "application/javascript;charset=utf-8"
        elif path.endswith(".css"):
            content_type = "text/css;charset=utf-8"
        elif path.endswith(".json") or path.endswith(".map"):
            content_type = "application/json;charset=utf-8"
        elif path.endswith(".svg"):
            content_type = "image/svg+xml"
        elif path.endswith(".png"):
            content_type = "image/png"
        elif path.endswith(".ico"):
            content_type = "image/x-icon"

        return Response(
            content,
            content_type=content_type,
            headers=[("Cache-Control", "public, max-age=31536000, immutable")],
        )

    @http.route(
        ["/api/graph", "/ormgraph/api/graph"], type="http", auth="user", methods=["GET"], cors="*"
    )
    def get_live_graph_http(self, **kwargs):
        data = self._build_graph_payload()
        return Response(json.dumps(data), content_type="application/json;charset=utf-8")

    @http.route(
        ["/api/graph/json", "/ormgraph/api/graph/json"],
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def get_live_graph_json(self, **kwargs):
        return self._build_graph_payload()

    @http.route(
        ["/api/path", "/ormgraph/api/path"], type="http", auth="user", methods=["GET"], cors="*"
    )
    def get_model_path(self, source=None, target=None, all=False, **kwargs):
        if not source or not target:
            return Response(
                json.dumps({"error": "Both source and target models are required"}),
                status=400,
                content_type="application/json",
            )

        graph_data = self._build_graph_payload()
        path = self._bfs_shortest_path(graph_data, source, target)

        if not path:
            return Response(
                json.dumps(
                    {
                        "path": None,
                        "paths": [],
                        "message": f"No path found between {source} and {target}",
                    }
                ),
                content_type="application/json",
            )

        return Response(
            json.dumps({"path": path, "paths": [path] if path else []}),
            content_type="application/json",
        )

    @http.route(
        ["/api/metrics", "/ormgraph/api/metrics"],
        type="http",
        auth="user",
        methods=["GET"],
        cors="*",
    )
    def get_metrics(self, **kwargs):
        graph_data = self._build_graph_payload()
        models = graph_data.get("models", [])
        rels = graph_data.get("relationships", [])

        degree_map = {}
        for r in rels:
            s, t = r["source"], r["target"]
            degree_map[s] = degree_map.get(s, 0) + 1
            degree_map[t] = degree_map.get(t, 0) + 1

        sorted_connected = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)[:10]

        metrics = {
            "total_models": len(models),
            "total_fields": sum(len(m.get("fields", [])) for m in models),
            "total_relationships": len(rels),
            "framework": "odoo",
            "most_connected": [{"model": k, "degree": v} for k, v in sorted_connected],
        }
        return Response(json.dumps(metrics), content_type="application/json")

    def _build_graph_payload(self) -> dict:
        env = request.env
        models_data = []
        relationships_data = []
        inheritance_edges = []

        module_map = {}
        try:
            domain = [("model", "=", "ir.model")]
            imd_records = env["ir.model.data"].sudo().search(domain)
            for imd in imd_records:
                module_map[imd.name.replace("model_", "").replace("_", ".")] = imd.module
        except Exception as e:
            _logger.debug("Could not fetch ir.model.data module mapping: %s", e)

        for model_name, model_cls in env.items():
            if not isinstance(model_name, str) or model_name.startswith("_"):
                continue

            fields_list = []
            incoming = []
            outgoing = []

            for fname, field in model_cls._fields.items():
                ftype = getattr(field, "type", "unknown")
                comodel = getattr(field, "comodel_name", None)

                fields_list.append(
                    {
                        "name": fname,
                        "type": ftype,
                        "field_type": ftype,
                        "comodel": comodel,
                        "comodel_name": comodel,
                        "required": getattr(field, "required", False),
                        "readonly": getattr(field, "readonly", False),
                        "computed": bool(getattr(field, "compute", False)),
                        "stored": getattr(field, "store", True),
                    }
                )

                if comodel and comodel in env:
                    rel_id = f"{model_name}::{fname}::{comodel}"
                    relationships_data.append(
                        {
                            "id": rel_id,
                            "source": model_name,
                            "target": comodel,
                            "field": fname,
                            "type": ftype,
                        }
                    )
                    outgoing.append({"to": comodel, "field": fname, "type": ftype})

            inherits_parents = getattr(model_cls, "_inherit", [])
            if isinstance(inherits_parents, str):
                inherits_parents = [inherits_parents]
            elif not isinstance(inherits_parents, (list, tuple)):
                inherits_parents = []

            for parent in inherits_parents:
                if parent and parent != model_name and parent in env:
                    inheritance_edges.append(
                        {
                            "id": f"inh::{model_name}::{parent}",
                            "child": model_name,
                            "parent": parent,
                            "type": "classical",
                        }
                    )

            delegations = getattr(model_cls, "_inherits", {})
            if isinstance(delegations, dict):
                for parent_model, field_via in delegations.items():
                    if parent_model in env:
                        inheritance_edges.append(
                            {
                                "id": f"inh_del::{model_name}::{parent_model}",
                                "child": model_name,
                                "parent": parent_model,
                                "type": "delegation",
                                "via_field": field_via,
                            }
                        )

            module_name = (
                module_map.get(model_name)
                or getattr(model_cls, "_original_module", None)
                or "custom"
            )

            models_data.append(
                {
                    "id": model_name,
                    "name": getattr(model_cls, "_description", None) or model_name,
                    "framework": "odoo",
                    "table": getattr(model_cls, "_table", None),
                    "table_name": getattr(model_cls, "_table", None),
                    "module": module_name,
                    "abstract": getattr(model_cls, "_abstract", False),
                    "transient": getattr(model_cls, "_transient", False),
                    "fields": fields_list,
                    "incoming": incoming,
                    "outgoing": outgoing,
                }
            )

        return {
            "framework": "odoo",
            "root_path": "Live Odoo Registry",
            "models": models_data,
            "relationships": relationships_data,
            "inheritance_edges": inheritance_edges,
            "stats": {
                "models": len(models_data),
                "relationships": len(relationships_data),
                "inheritance_edges": len(inheritance_edges),
            },
        }

    def _bfs_shortest_path(self, graph_data: dict, start: str, target: str) -> dict | None:
        adj = {}
        for r in graph_data.get("relationships", []):
            s, t, f, tp = r["source"], r["target"], r["field"], r["type"]
            adj.setdefault(s, []).append((t, f, tp))

        queue = deque([(start, [start], [])])
        visited = {start}

        while queue:
            current, path_nodes, path_edges = queue.popleft()
            if current == target:
                return {
                    "nodes": path_nodes,
                    "edges": path_edges,
                    "length": len(path_edges),
                }

            for neighbor, field_name, rel_type in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_info = {
                        "source": current,
                        "target": neighbor,
                        "field": field_name,
                        "type": rel_type,
                    }
                    queue.append((neighbor, [*path_nodes, neighbor], [*path_edges, edge_info]))

        return None
