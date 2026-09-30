class JsonifierTestDataMixin:
    @classmethod
    def _create_demo_export_class(cls):
        cls.ir_exp_partner = cls.env["ir.exports"].create(
            {
                "name": "Partner Export",
                "resource": "res.partner",
            }
        )
        return cls.ir_exp_partner

    @classmethod
    def _create_demo_export_lines_class(cls):
        export_lines_data = [
            {"name": "name"},
            {"name": "active"},
            {"name": "partner_latitude"},
            {"name": "color"},
            {"name": "category_id/name"},
            {"name": "country_id/name"},
            {"name": "country_id/code"},
            {"name": "child_ids/name"},
            {"name": "child_ids/id"},
            {"name": "child_ids/email"},
            {"name": "child_ids/country_id/name"},
            {"name": "child_ids/country_id/code"},
            {"name": "child_ids/child_ids/name"},
            {"name": "lang"},
            {"name": "comment"},
        ]

        export_lines = cls.env["ir.exports.line"]

        for line_data in export_lines_data:
            line_data["export_id"] = cls.ir_exp_partner.id
            line = cls.env["ir.exports.line"].create(line_data)
            export_lines |= line

        return export_lines

    @classmethod
    def _create_demo_resolver_class(cls):
        python_code = """is_number = field_type in ('integer', 'float')
ftype = "NUMBER" if is_number else "TEXT"
value = value if is_number else str(value)
result = {"Key": name, "Value": value, "Type": ftype, "IsPublic": True}"""

        cls.ir_exports_resolver_dict = cls.env["ir.exports.resolver"].create(
            {
                "name": "ExtraData dictionary (number/text)",
                "python_code": python_code,
            }
        )
        return cls.ir_exports_resolver_dict

    @classmethod
    def setUpClass_demo_data(cls):
        cls._create_demo_export_class()
        cls._create_demo_export_lines_class()
        cls._create_demo_resolver_class()
