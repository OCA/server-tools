#!/usr/bin/env python
import logging

_logger = logging.getLogger(__name__)

black_list = [
    "ir.actions.actions",
    "ir.actions.act_window.view",
    "ir.actions.act_window",
    "ir.ui.view",
    "ir.actions.server",
    "ir.server.object.lines",
    "ir.actions.report",
    "res.lang",
    "ir.filters",
    "ir.module.category",
    "res.users",
    "res.company",
    "res.currency",
    "ir.actions.client",
    "res.country",
    "res.country.state" "ir.module.module",
]


def _check_action_profiled_user(env, uid, name, action, model, operation="python"):
    action_id = action.get("id")
    user = env["res.users"].sudo().browse(uid)
    if user.is_profiled and model:
        session = user.active_session_id
        if "res.users.profile" in model:
            return
        rec = (
            env["res.users.profiler.actions"]
            .sudo()
            .search(
                [
                    "&",
                    "&",
                    "&",
                    ("session_id", "=", session.id),
                    ("res_model", "=", model),
                    ("action_type", "=", operation),
                    ("action_name", "=", name),
                ],
                limit=1,
            )
        )
        if not rec:
            values = {
                "session_id": session.id,
                "user_id": uid,
                "res_model": model,
                "action_name": name,
                "action_type": operation,
            }
            if action_id:
                values["action_id"] = action_id
            env["res.users.profiler.actions"].sudo().create(values)


def _is_basic_access_right(env, access_right):
    basic_security_group = (
        env["res.groups"].sudo().search([("name", "=", "Internal User")])
    )
    basic_access_rights = basic_security_group.model_access
    ar_perms = []
    if access_right.perm_read:
        ar_perms.append("r")
    if access_right.perm_write:
        ar_perms.append("w")
    if access_right.perm_create:
        ar_perms.append("c")
    if access_right.perm_unlink:
        ar_perms.append("u")

    for bar in basic_access_rights:
        is_basic = False
        model_name = bar.model_id.model
        if model_name == access_right.res_model:
            bar_perms = []
            if bar.perm_read:
                bar_perms.append("r")
            if bar.perm_write:
                bar_perms.append("w")
            if bar.perm_create:
                bar_perms.append("c")
            if bar.perm_unlink:
                bar_perms.append("u")
            ar_perms_set = set(ar_perms)
            bar_perms_set = set(bar_perms)
            if ar_perms_set.issubset(bar_perms_set):
                is_basic = True
                break
    return is_basic


def _postprocess_check_access_rights(env, active_user_session):
    profiled_accesses_ids = []
    for ar in active_user_session.profiled_accesses_ids:
        if not (ar.res_model in black_list) and not (_is_basic_access_right(env, ar)):
            profiled_accesses_ids.append(ar.id)
    return profiled_accesses_ids


def _check_access_profiled_user(env, operation, model):
    user = env.user
    if user.is_profiled and model:
        session = user.active_session_id
        if (
            ("res.users.profile" in model)
            or ("bus" in model)
            or ("template.security.group" in model)
        ):
            return
        rec = (
            env["res.users.profiler.accesses"]
            .sudo()
            .search(
                [
                    "&",
                    ("session_id", "=", session.id),
                    ("res_model", "=", model),
                ],
                limit=1,
            )
        )

        if rec:
            if operation == "write":
                if not rec.perm_write:
                    rec.sudo().write(
                        {
                            "perm_write": True,
                        }
                    )
            elif operation == "create":
                if not rec.perm_create:
                    rec.sudo().write(
                        {
                            "perm_create": True,
                        }
                    )
            elif (
                operation == "read"
                or operation == "load_views"
                or operation == "read_group"
            ):
                if not rec.perm_read:
                    rec.sudo().write(
                        {
                            "perm_read": True,
                        }
                    )
            elif operation == "unlink":
                if not rec.perm_unlink:
                    rec.sudo().write(
                        {
                            "perm_unlink": True,
                        }
                    )
        else:
            values = {
                "session_id": session.id,
                "user_id": user.id,
                "res_model": model,
            }
            if operation == "write":
                values["perm_write"] = True
                env["res.users.profiler.accesses"].sudo().create(values)
            elif operation == "create":
                values["perm_create"] = True
                env["res.users.profiler.accesses"].sudo().create(values)
            elif (
                operation == "read"
                or operation == "load_views"
                or operation == "read_group"
            ):
                values["perm_read"] = True
                env["res.users.profiler.accesses"].sudo().create(values)
            elif operation == "unlink":
                values["perm_unlink"] = True
                env["res.users.profiler.accesses"].sudo().create(values)
