# Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class SecurityAnalyzer(models.AbstractModel):
    """Core security analysis logic - stateless pure functions"""

    _name = "security.analyzer"
    _description = "Security Analysis Logic"

    @api.model
    def _is_base_user_role_installed(self):
        """Check if base_user_role module is installed"""
        return "res.users.role" in self.env

    @api.model
    def analyze_model_access(self, model_name, user_id, operation="read"):
        """
        Analyze ACL (ir.model.access) for a user on a model.

        Args:
            model_name (str): Technical model name (e.g., 'sale.order')
            user_id (int): User ID to check
            operation (str): One of 'read', 'write', 'create', 'unlink'

        Returns:
            dict: {
                'has_access': bool,
                'applicable_rules': list of dicts with rule details,
                'explanation': str,
                'operation': str
            }
        """
        user = self.env["res.users"].browse(user_id)
        user_groups = user.groups_id

        # Get all access rights for this model
        access_rights = (
            self.env["ir.model.access"]
            .sudo()
            .search([("model_id.model", "=", model_name)])
        )

        applicable_rules = []
        has_access = False
        perm_field = f"perm_{operation}"

        for access in access_rights:
            # Check if this access right applies to the user
            applies = False
            rule_info = {
                "id": access.id,
                "name": access.name,
                "model": model_name,
                "group": access.group_id.full_name
                if access.group_id
                else _("All Users (Global)"),
                "group_id": access.group_id.id if access.group_id else False,
                "permissions": {
                    "read": access.perm_read,
                    "write": access.perm_write,
                    "create": access.perm_create,
                    "unlink": access.perm_unlink,
                },
                "grants_access": False,
                "applies_to_user": False,
            }

            # Global rule (no group) applies to everyone
            if not access.group_id:
                applies = True
            # Group-specific rule
            elif access.group_id in user_groups:
                applies = True

            rule_info["applies_to_user"] = applies

            if applies and getattr(access, perm_field):
                rule_info["grants_access"] = True
                has_access = True

            applicable_rules.append(rule_info)

        # Generate explanation
        if has_access:
            granting_rules = [r for r in applicable_rules if r["grants_access"]]
            explanation = _(
                "User '%(user)s' has %(operation)s access to model"
                " '%(model)s' via %(count)d access rule(s)."
            ) % {
                "user": user.name,
                "operation": operation,
                "model": model_name,
                "count": len(granting_rules),
            }
        else:
            explanation = _(
                "User '%(user)s' does NOT have %(operation)s access"
                " to model '%(model)s'. No applicable access rules"
                " grant this permission."
            ) % {
                "user": user.name,
                "operation": operation,
                "model": model_name,
            }

        return {
            "has_access": has_access,
            "applicable_rules": applicable_rules,
            "explanation": explanation,
            "operation": operation,
            "user": user.name,
            "model": model_name,
        }

    @api.model
    def analyze_record_rules(self, model_name, user_id, operation="read"):
        """
        Analyze record rules (ir.rule) for a user on a model.

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            operation (str): One of 'read', 'write', 'create', 'unlink'

        Returns:
            dict: {
                'rules': list of rule details,
                'global_rules': list of global rules (AND logic),
                'group_rules': list of group rules (OR logic),
                'explanation': str
            }
        """
        user = self.env["res.users"].browse(user_id)
        user_groups = user.groups_id

        # Get all record rules for this model
        record_rules = (
            self.env["ir.rule"].sudo().search([("model_id.model", "=", model_name)])
        )

        global_rules = []
        group_rules = []
        perm_field = f"perm_{operation}"

        for rule in record_rules:
            # Check if this rule applies to the operation
            if not getattr(rule, perm_field):
                continue

            rule_info = {
                "id": rule.id,
                "name": rule.name,
                "domain": rule.domain_force,
                "global": getattr(rule, "global"),
                "groups": [g.full_name for g in rule.groups],
                "group_ids": rule.groups.ids,
                "perm_read": rule.perm_read,
                "perm_write": rule.perm_write,
                "perm_create": rule.perm_create,
                "perm_unlink": rule.perm_unlink,
                "applies_to_user": False,
            }

            # Global rules apply to everyone
            if getattr(rule, "global"):
                rule_info["applies_to_user"] = True
                global_rules.append(rule_info)
            # Group rules only apply if user is in one of the groups
            elif any(group in user_groups for group in rule.groups):
                rule_info["applies_to_user"] = True
                group_rules.append(rule_info)

        # Generate explanation
        explanation_parts = []

        if global_rules:
            explanation_parts.append(
                _("%d global rule(s) apply (ALL must be satisfied - AND logic)")
                % len(global_rules)
            )

        if group_rules:
            explanation_parts.append(
                _("%d group-specific rule(s) apply (ANY can grant access - OR logic)")
                % len(group_rules)
            )

        if not global_rules and not group_rules:
            explanation_parts.append(_("No record rules apply to this model"))

        return {
            "rules": global_rules + group_rules,
            "global_rules": global_rules,
            "group_rules": group_rules,
            "explanation": ". ".join(explanation_parts) + ".",
            "user": user.name,
            "model": model_name,
            "operation": operation,
        }

    @api.model
    def explain_access_decision(
        self, model_name, user_id, record_id=None, operation="read"
    ):
        """
        Comprehensive explanation of access decision.

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            record_id (int, optional): Specific record ID to check
            operation (str): Operation to check

        Returns:
            dict: Complete analysis with step-by-step explanation
        """
        # Step 1: Analyze model-level access (ACL)
        model_access = self.analyze_model_access(model_name, user_id, operation)

        # Step 2: Analyze record rules
        record_rules = self.analyze_record_rules(model_name, user_id, operation)

        # Step 3: If record_id provided, simulate actual access
        simulation_result = None
        if record_id:
            simulation_result = self.simulate_user_access(
                user_id, model_name, record_id, operation
            )

        # Generate final verdict
        if not model_access["has_access"]:
            final_verdict = "denied"
            verdict_explanation = (
                _("Access DENIED: User lacks model-level %s permission") % operation
            )
        elif record_rules["global_rules"] or record_rules["group_rules"]:
            if simulation_result:
                final_verdict = (
                    "allowed" if simulation_result["has_access"] else "denied"
                )
                verdict_explanation = simulation_result["explanation"]
            else:
                final_verdict = "conditional"
                verdict_explanation = _(
                    "Model access granted, but record rules"
                    " apply. Specific records may be filtered."
                )
        else:
            final_verdict = "allowed"
            verdict_explanation = _(
                "Access ALLOWED: User has model permission"
                " and no record rules restrict access"
            )

        return {
            "model_access": model_access,
            "record_rules": record_rules,
            "simulation": simulation_result,
            "final_verdict": final_verdict,
            "verdict_explanation": verdict_explanation,
            "steps": [
                {
                    "step": 1,
                    "title": _("Model-Level Access (ACL)"),
                    "result": _("Allowed")
                    if model_access["has_access"]
                    else _("Denied"),
                    "details": model_access["explanation"],
                },
                {
                    "step": 2,
                    "title": _("Record Rules"),
                    "result": _("No rules")
                    if not record_rules["rules"]
                    else _("%d rules apply") % len(record_rules["rules"]),
                    "details": record_rules["explanation"],
                },
            ],
        }

    @api.model
    def simulate_user_access(self, user_id, model_name, record_id, operation="read"):
        """
        Simulate access check for a specific user and record (safe, read-only).

        Args:
            user_id (int): User ID
            model_name (str): Model name
            record_id (int): Record ID
            operation (str): Operation

        Returns:
            dict: Simulation result with explanation
        """
        user = self.env["res.users"].browse(user_id)

        try:
            # Get the record
            model = self.env[model_name]
            record = model.browse(record_id).exists()

            if not record:
                return {
                    "has_access": False,
                    "explanation": _(
                        "Record ID %(record_id)d does not exist" " in model '%(model)s'"
                    )
                    % {"record_id": record_id, "model": model_name},
                    "error": "record_not_found",
                }

            # Simulate as the target user
            record_as_user = record.with_user(user)

            # Check model-level access
            try:
                record_as_user.check_access_rights(operation)
            except AccessError as e:
                return {
                    "has_access": False,
                    "explanation": _("Model-level access denied: %s") % str(e),
                    "error": "model_access_denied",
                }

            # Check record-level access
            try:
                record_as_user.check_access_rule(operation)
                return {
                    "has_access": True,
                    "explanation": _(
                        "User '%(user)s' has %(operation)s access"
                        " to record #%(record_id)d of"
                        " model '%(model)s'"
                    )
                    % {
                        "user": user.name,
                        "operation": operation,
                        "record_id": record_id,
                        "model": model_name,
                    },
                    "error": None,
                }
            except AccessError as e:
                return {
                    "has_access": False,
                    "explanation": _("Record rule denied access: %s") % str(e),
                    "error": "record_rule_denied",
                }

        except Exception as e:
            _logger.exception("Error simulating user access")
            return {
                "has_access": False,
                "explanation": _("Simulation error: %s") % str(e),
                "error": "simulation_error",
            }

    @api.model
    def get_access_matrix(self, user_ids=None, model_ids=None, operations=None):
        """
        Generate access matrix for multiple users and models.

        Args:
            user_ids (list, optional): List of user IDs.
                If None or empty, return empty matrix.
            model_ids (list, optional): List of model IDs.
                If None or empty, return empty matrix.
            operations (list, optional): List of operations.
                Default: ['read', 'write', 'create', 'unlink']

        Returns:
            dict: Matrix data structure for visualization
        """
        if operations is None:
            operations = ["read", "write", "create", "unlink"]

        # Get users - NO DEFAULTS
        if user_ids:
            users = self.env["res.users"].browse(user_ids)
        else:
            users = self.env["res.users"]  # Empty recordset

        # Get models - NO DEFAULTS
        if model_ids:
            models = self.env["ir.model"].browse(model_ids)
        else:
            models = self.env["ir.model"]  # Empty recordset

        # Build matrix
        matrix = {
            "users": [{"id": u.id, "name": u.name, "login": u.login} for u in users],
            "models": [{"id": m.id, "name": m.name, "model": m.model} for m in models],
            "operations": operations,
            "cells": {},  # Key: "user_id,model_id,operation" -> value: bool
        }

        # Calculate access for each combination (only if both users and models exist)
        for user in users:
            for model in models:
                for operation in operations:
                    key = f"{user.id},{model.id},{operation}"
                    analysis = self.analyze_model_access(
                        model.model, user.id, operation
                    )
                    matrix["cells"][key] = {
                        "has_access": analysis["has_access"],
                        "rule_count": len(analysis["applicable_rules"]),
                    }

        return matrix

    @api.model
    def get_user_accessible_models(self, user_id, operation="read"):
        """
        List all models a user can access.

        Args:
            user_id (int): User ID
            operation (str): Operation to check

        Returns:
            list: List of accessible model names with details
        """
        user = self.env["res.users"].browse(user_id)
        user_groups = user.groups_id

        # Get all access rights
        access_rights = self.env["ir.model.access"].sudo().search([])
        perm_field = f"perm_{operation}"

        accessible_models = {}

        for access in access_rights:
            if not getattr(access, perm_field):
                continue

            # Check if applies to user
            if not access.group_id or access.group_id in user_groups:
                model_name = access.model_id.model
                if model_name not in accessible_models:
                    accessible_models[model_name] = {
                        "model": model_name,
                        "name": access.model_id.name,
                        "access_rules": [],
                    }
                accessible_models[model_name]["access_rules"].append(access.name)

        return list(accessible_models.values())

    @api.model
    def analyze_multicompany_access(self, model_name, user_id, operation="read"):
        """
        Analyze multi-company security for a user on a model.

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            operation (str): Operation to check

        Returns:
            dict: Multi-company analysis with company-specific rules
        """
        user = self.env["res.users"].browse(user_id)

        # Get user's companies
        user_companies = user.company_ids
        current_company = user.company_id

        # Check if model has company_id field
        model_obj = self.env[model_name]
        has_company_field = "company_id" in model_obj._fields

        # Get company-related record rules
        record_rules = (
            self.env["ir.rule"].sudo().search([("model_id.model", "=", model_name)])
        )

        company_rules = []
        perm_field = f"perm_{operation}"

        for rule in record_rules:
            if not getattr(rule, perm_field):
                continue

            # Check if rule has company-related domain
            domain = rule.domain_force or "[]"
            if "company_id" in domain or "company_ids" in domain:
                rule_info = {
                    "id": rule.id,
                    "name": rule.name,
                    "domain": domain,
                    "global": getattr(rule, "global"),
                    "groups": [g.full_name for g in rule.groups],
                    "applies_to_user": False,
                }

                # Check if rule applies to user
                if getattr(rule, "global"):
                    rule_info["applies_to_user"] = True
                elif any(group in user.groups_id for group in rule.groups):
                    rule_info["applies_to_user"] = True

                if rule_info["applies_to_user"]:
                    company_rules.append(rule_info)

        # Analyze accessible companies
        accessible_companies = []
        if has_company_field:
            # Try to determine which companies the user can access records from
            for company in user_companies:
                accessible_companies.append(
                    {
                        "id": company.id,
                        "name": company.name,
                        "is_current": company.id == current_company.id,
                    }
                )

        return {
            "user": user.name,
            "user_id": user_id,
            "model": model_name,
            "operation": operation,
            "has_company_field": has_company_field,
            "user_companies": [
                {"id": c.id, "name": c.name, "is_current": c.id == current_company.id}
                for c in user_companies
            ],
            "current_company": {"id": current_company.id, "name": current_company.name},
            "company_rules": company_rules,
            "accessible_companies": accessible_companies,
            "explanation": self._generate_multicompany_explanation(
                user, model_name, has_company_field, company_rules, user_companies
            ),
        }

    def _generate_multicompany_explanation(
        self, user, model_name, has_company_field, company_rules, user_companies
    ):
        """Generate human-readable explanation of multi-company access"""
        explanation_parts = []

        explanation_parts.append(
            _("User '%(user)s' belongs to" " %(count)d company/companies.")
            % {"user": user.name, "count": len(user_companies)}
        )

        if has_company_field:
            explanation_parts.append(
                _("Model '%s' has a company_id field, so access is company-restricted.")
                % model_name
            )
        else:
            explanation_parts.append(
                _("Model '%s' does not have a company_id field (company-independent).")
                % model_name
            )

        if company_rules:
            explanation_parts.append(
                _("%d company-related record rule(s) apply to this model.")
                % len(company_rules)
            )
        else:
            explanation_parts.append(
                _("No company-specific record rules found for this model.")
            )

        if has_company_field and user_companies:
            company_names = ", ".join([c.name for c in user_companies])
            explanation_parts.append(
                _("User can access records from these companies: %s") % company_names
            )

        return " ".join(explanation_parts)

    @api.model
    def get_company_access_matrix(self, user_id, company_ids=None):
        """
        Generate access matrix showing permissions per company.

        Args:
            user_id (int): User ID
            company_ids (list, optional): List of company IDs to analyze

        Returns:
            dict: Matrix data showing access per company
        """
        user = self.env["res.users"].browse(user_id)

        # Get companies to analyze
        if company_ids:
            companies = self.env["res.company"].browse(company_ids)
        else:
            companies = user.company_ids

        # Find models with company_id field
        models_with_company = []
        common_models = [
            "sale.order",
            "purchase.order",
            "account.move",
            "stock.picking",
            "project.project",
            "hr.employee",
        ]

        for model_name in common_models:
            try:
                if (
                    model_name in self.env
                    and "company_id" in self.env[model_name]._fields
                ):
                    model = self.env["ir.model"].search(
                        [("model", "=", model_name)], limit=1
                    )
                    if model:
                        models_with_company.append(
                            {"id": model.id, "name": model.name, "model": model.model}
                        )
            except KeyError:
                continue

        # Build matrix
        matrix = {
            "user": {"id": user.id, "name": user.name},
            "companies": [{"id": c.id, "name": c.name} for c in companies],
            "models": models_with_company,
            "cells": {},  # Key: "company_id,model_id" -> analysis
        }

        # Analyze each combination
        for company in companies:
            for model_dict in models_with_company:
                key = f"{company.id},{model_dict['id']}"

                analysis = self.analyze_multicompany_access(
                    model_dict["model"], user_id, "read"
                )

                matrix["cells"][key] = {
                    "has_access": company.id
                    in [c["id"] for c in analysis["user_companies"]],
                    "company_rules": len(analysis["company_rules"]),
                }

        return matrix

    @api.model
    def analyze_user_roles(self, user_id):
        """
        Analyze user's roles if base_user_role module is installed.

        Args:
            user_id (int): User ID

        Returns:
            dict: Role analysis with groups granted by each role
        """
        if not self._is_base_user_role_installed():
            return {
                "module_installed": False,
                "roles": [],
                "explanation": _(
                    "Module 'base_user_role' is not installed."
                    " Install it to use role-based access"
                    " analysis."
                ),
            }

        user = self.env["res.users"].browse(user_id)

        # Get user's roles
        user_roles = (
            self.env["res.users.role"]
            .sudo()
            .search([("line_ids.user_id", "=", user_id)])
        )

        roles_data = []
        all_groups_from_roles = self.env["res.groups"]

        for role in user_roles:
            role_groups = role.group_id + role.implied_ids
            all_groups_from_roles |= role_groups

            roles_data.append(
                {
                    "id": role.id,
                    "name": role.name,
                    "groups": [{"id": g.id, "name": g.full_name} for g in role_groups],
                    "group_count": len(role_groups),
                }
            )

        # Groups granted directly (not through roles)
        direct_groups = user.groups_id - all_groups_from_roles

        return {
            "module_installed": True,
            "user": user.name,
            "user_id": user_id,
            "roles": roles_data,
            "role_count": len(user_roles),
            "groups_from_roles": [
                {"id": g.id, "name": g.full_name} for g in all_groups_from_roles
            ],
            "direct_groups": [{"id": g.id, "name": g.full_name} for g in direct_groups],
            "total_groups": len(user.groups_id),
            "explanation": self._generate_role_explanation(
                user, user_roles, all_groups_from_roles, direct_groups
            ),
        }

    def _generate_role_explanation(self, user, roles, groups_from_roles, direct_groups):
        """Generate human-readable explanation of role-based access"""
        explanation_parts = []

        if roles:
            explanation_parts.append(
                _("User '%(user)s' has %(count)d" " role(s) assigned.")
                % {"user": user.name, "count": len(roles)}
            )

            explanation_parts.append(
                _("These roles grant %(count)d group(s) in total.")
                % {"count": len(groups_from_roles)}
            )
        else:
            explanation_parts.append(
                _("User '%(user)s' has no roles assigned.") % {"user": user.name}
            )

        if direct_groups:
            explanation_parts.append(
                _(
                    "Additionally, user has %(count)d group(s)"
                    " assigned directly (not through roles)."
                )
                % {"count": len(direct_groups)}
            )

        explanation_parts.append(
            _("Total effective groups: %(count)d") % {"count": len(user.groups_id)}
        )

        return " ".join(explanation_parts)

    @api.model
    def analyze_model_access_with_roles(self, model_name, user_id, operation="read"):
        """
        Extended model access analysis that includes role information.

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            operation (str): Operation to check

        Returns:
            dict: Enhanced analysis with role information
        """
        # Get standard access analysis
        base_analysis = self.analyze_model_access(model_name, user_id, operation)

        # Add role information if module is installed
        if not self._is_base_user_role_installed():
            base_analysis["role_analysis"] = {
                "module_installed": False,
                "roles_granting_access": [],
            }
            return base_analysis

        # Analyze which roles grant access
        user = self.env["res.users"].browse(user_id)
        user_roles = (
            self.env["res.users.role"]
            .sudo()
            .search([("line_ids.user_id", "=", user_id)])
        )

        roles_granting_access = []

        for role in user_roles:
            role_groups = role.group_id + role.implied_ids

            # Check if any of this role's groups grant access
            for rule in base_analysis["applicable_rules"]:
                if rule["grants_access"] and rule["applies_to_user"]:
                    if rule["group_id"] and rule["group_id"] in role_groups.ids:
                        if role.id not in [r["id"] for r in roles_granting_access]:
                            roles_granting_access.append(
                                {
                                    "id": role.id,
                                    "name": role.name,
                                    "grants_via_group": rule["group"],
                                }
                            )

        base_analysis["role_analysis"] = {
            "module_installed": True,
            "roles_granting_access": roles_granting_access,
            "explanation": self._generate_role_access_explanation(
                user, roles_granting_access, base_analysis["has_access"]
            ),
        }

        return base_analysis

    def _generate_role_access_explanation(
        self, user, roles_granting_access, has_access
    ):
        """Generate explanation of role-based access grants"""
        if not has_access:
            return _(
                "User does not have access (no roles grant the required permission)."
            )

        if not roles_granting_access:
            return _("Access granted through direct group membership (not via roles).")

        role_names = ", ".join([r["name"] for r in roles_granting_access])
        return _("Access granted through %(count)d role(s):" " %(roles)s") % {
            "count": len(roles_granting_access),
            "roles": role_names,
        }

    @api.model
    def explain_access_decision_with_roles(
        self, model_name, user_id, record_id=None, operation="read"
    ):
        """
        Comprehensive explanation including role information.

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            record_id (int, optional): Specific record ID
            operation (str): Operation to check

        Returns:
            dict: Complete analysis with role information
        """
        # Get base explanation
        explanation = self.explain_access_decision(
            model_name, user_id, record_id, operation
        )

        # Enhance with role analysis
        if self._is_base_user_role_installed():
            role_analysis = self.analyze_user_roles(user_id)
            model_access_with_roles = self.analyze_model_access_with_roles(
                model_name, user_id, operation
            )

            explanation["role_analysis"] = role_analysis
            explanation["model_access"]["role_details"] = model_access_with_roles.get(
                "role_analysis", {}
            )

            # Add role step to explanation steps
            if role_analysis["role_count"] > 0:
                explanation["steps"].insert(
                    0,
                    {
                        "step": 0,
                        "title": _("User Roles"),
                        "result": _("%d roles assigned") % role_analysis["role_count"],
                        "details": role_analysis["explanation"],
                    },
                )

        return explanation

    @api.model
    def analyze_crud_summary(self, model_name, user_id, record_id=None):
        """
        Comprehensive CRUD analysis - all 4 operations with conflict detection.

        This is the KEY method that shows:
        1. Final YES/NO for each CRUD operation
        2. Conflicts between groups (Group A says YES, Group B says NO)
        3. How Odoo resolves conflicts (OR logic - ANY group grants access)
        4. Clear summary table

        Args:
            model_name (str): Technical model name
            user_id (int): User ID
            record_id (int, optional): Specific record ID to test

        Returns:
            dict: {
                'operations': {
                    'create': {'allowed': bool, 'conflicts': list, 'explanation': str},
                    'read': {...},
                    'write': {...},
                    'unlink': {...}
                },
                'conflicts_detected': bool,
                'conflict_explanation': str,
                'summary_table': list of operation summaries
            }
        """
        user = self.env["res.users"].browse(user_id)
        user_groups = user.groups_id
        operations = ["create", "read", "write", "unlink"]

        results = {}
        conflicts_detected = False
        conflict_details = []

        for operation in operations:
            # Get all access rights for this model and operation
            access_rights = (
                self.env["ir.model.access"]
                .sudo()
                .search([("model_id.model", "=", model_name)])
            )

            perm_field = f"perm_{operation}"
            granting_groups = []
            denying_groups = []
            global_grants = False

            for access in access_rights:
                has_permission = getattr(access, perm_field)

                # Global rule (no group)
                if not access.group_id:
                    if has_permission:
                        global_grants = True
                        granting_groups.append(
                            {
                                "name": _("All Users (Global)"),
                                "rule_name": access.name,
                                "grants": True,
                            }
                        )
                    else:
                        denying_groups.append(
                            {
                                "name": _("All Users (Global)"),
                                "rule_name": access.name,
                                "grants": False,
                            }
                        )
                # Group-specific rule
                elif access.group_id in user_groups:
                    if has_permission:
                        granting_groups.append(
                            {
                                "name": access.group_id.full_name,
                                "rule_name": access.name,
                                "grants": True,
                            }
                        )
                    else:
                        denying_groups.append(
                            {
                                "name": access.group_id.full_name,
                                "rule_name": access.name,
                                "grants": False,
                            }
                        )

            # ODOO LOGIC: If ANY group grants access, user has access (OR logic)
            final_allowed = bool(granting_groups) or global_grants

            # Detect conflicts
            has_conflict = bool(granting_groups) and bool(denying_groups)
            if has_conflict:
                conflicts_detected = True
                conflict_details.append(
                    {
                        "operation": operation.upper(),
                        "granting": [g["name"] for g in granting_groups],
                        "denying": [d["name"] for d in denying_groups],
                    }
                )

            # Build explanation
            if not granting_groups and not denying_groups:
                explanation = (
                    _("No access rules apply to this user for %s operation.")
                    % operation.upper()
                )
                final_allowed = False
            elif global_grants:
                explanation = (
                    _("✓ GRANTED: Global rule grants %s access to all users.")
                    % operation.upper()
                )
            elif granting_groups and not has_conflict:
                group_names = ", ".join([g["name"] for g in granting_groups])
                explanation = _(
                    "GRANTED: User's groups (%(groups)s)" " grant %(operation)s access."
                ) % {
                    "groups": group_names,
                    "operation": operation.upper(),
                }
            elif has_conflict:
                grant_names = ", ".join([g["name"] for g in granting_groups])
                deny_names = ", ".join([d["name"] for d in denying_groups])
                explanation = _(
                    "CONFLICT RESOLVED: User belongs to groups"
                    " that GRANT access (%(grant)s) and groups"
                    " that DENY access (%(deny)s). RESULT:"
                    " ACCESS GRANTED (Odoo uses OR logic - if"
                    " ANY group grants access, user can"
                    " %(operation)s)."
                ) % {
                    "grant": grant_names,
                    "deny": deny_names,
                    "operation": operation.upper(),
                }
            elif denying_groups:
                deny_names = ", ".join([d["name"] for d in denying_groups])
                explanation = _(
                    "DENIED: User's groups (%(groups)s) do not"
                    " grant %(operation)s access."
                ) % {
                    "groups": deny_names,
                    "operation": operation.upper(),
                }
            else:
                explanation = (
                    _("✗ DENIED: No applicable rules grant %s access.")
                    % operation.upper()
                )

            results[operation] = {
                "allowed": final_allowed,
                "granting_groups": granting_groups,
                "denying_groups": denying_groups,
                "has_conflict": has_conflict,
                "explanation": explanation,
            }

        # Generate conflict summary
        if conflicts_detected:
            conflict_explanation = _(
                "IMPORTANT: Conflicts detected! User belongs"
                " to groups with contradicting permissions."
                " Odoo resolves this using OR logic: if ANY"
                " group grants access, the user CAN perform"
                " the operation. This means granting groups"
                " always win over denying groups."
            )
        else:
            conflict_explanation = _(
                "✓ No conflicts: All user's groups have consistent permissions."
            )

        # Build summary table
        summary_table = []
        for operation in operations:
            op_data = results[operation]
            summary_table.append(
                {
                    "operation": operation.upper(),
                    "operation_display": {
                        "create": _("Create"),
                        "read": _("Read"),
                        "write": _("Write/Update"),
                        "unlink": _("Delete"),
                    }[operation],
                    "allowed": op_data["allowed"],
                    "has_conflict": op_data["has_conflict"],
                    "granting_count": len(op_data["granting_groups"]),
                    "denying_count": len(op_data["denying_groups"]),
                    "verdict": _("✓ ALLOWED") if op_data["allowed"] else _("✗ DENIED"),
                    "verdict_class": "success" if op_data["allowed"] else "danger",
                }
            )

        return {
            "user": user.name,
            "user_id": user_id,
            "model": model_name,
            "operations": results,
            "conflicts_detected": conflicts_detected,
            "conflict_explanation": conflict_explanation,
            "conflict_details": conflict_details,
            "summary_table": summary_table,
            "odoo_logic_explanation": _(
                "Odoo Access Control Logic:\n"
                "1. Model Access (ACL): ANY group granting"
                " access = Access granted (OR logic)\n"
                "2. Record Rules: GLOBAL rules use AND logic"
                " (all must pass), GROUP rules use OR logic"
                " (any can grant)\n"
                "3. If you see conflicts, the granting"
                " permission always wins at the ACL level."
            ),
        }
