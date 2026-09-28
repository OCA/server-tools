# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


class IrExportsResolver:
    """
    The role of this class is to convert data of branches
    into a the form of data that jsonifer module can jsonify.

    I assume that the data coming from ir.exports record is looking like this:
    {
        'fields': [
            {'name': 'name'},
            (
                {'name': 'categ_id'},
                [{'name': 'name'}, {'name': 'sale_ok'}, {'name': 'purchase_ok'}]
            )
        ]
    }

    The final datastructure should look similar to this structure:
    ["id", "name", ("categ_id", ["id", "name", "sale_ok", "purchase_ok"])]
    """

    def __init__(self, parser):
        fields = []
        if parser.get("fields") and isinstance(parser["fields"], list):
            fields = parser["fields"]
        self.resolved_parser = [self.convert(field) for field in fields]
        # Remove elements from the list if they are empty lists
        self.resolved_parser = [item for item in self.resolved_parser if item]

    def get_dict_key(self, field):
        if isinstance(field, dict) and "name" in field:
            return field["name"]
        else:
            return field

    def resolve_tuple_field(self, field):
        if isinstance(field, tuple) and len(field) == 2:
            parent, children = field
            if isinstance(parent, dict):
                return (
                    self.get_dict_key(parent),
                    [
                        self.get_dict_key(child)
                        if isinstance(child, dict)
                        else self.resolve_tuple_field(child)
                        for child in children
                    ],
                )
        # Safeguarding the structure result if the branch is broken,
        # assign this branch empty list to protect other branches and the root
        return []

    def convert(self, field):
        if isinstance(field, dict):
            return self.get_dict_key(field)
        else:
            return self.resolve_tuple_field(field)
