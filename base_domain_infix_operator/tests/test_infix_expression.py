#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

from odoo.addons.base_domain_infix_operator.infix_expression import to_infix_domain


class TestInfixExpression(TransactionCase):
    def test_infix_domain(self):
        prefix_domain = [
            "!",
            "&",
            ("a", "=", "b"),
            "!",
            ("c", "=", "d"),
            "|",
            ("e", "=", "f"),
            "!",
            ("g", "=", "h"),
        ]
        infix_domain = to_infix_domain(prefix_domain)
        self.assertEqual(
            infix_domain,
            [
                (
                    (
                        "NOT",
                        (
                            ("a", "=", "b"),
                            "AND",
                            (
                                "NOT",
                                ("c", "=", "d"),
                            ),
                        ),
                    ),
                    "AND",
                    (
                        ("e", "=", "f"),
                        "OR",
                        (
                            "NOT",
                            ("g", "=", "h"),
                        ),
                    ),
                )
            ],
        )
