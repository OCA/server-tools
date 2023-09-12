def convert_simple_to_full_parser(parser):
    """Convert a simple API style parser to a full parser"""
    assert isinstance(parser, list)
    return {"fields": _convert_parser(parser)}


def _convert_field(fld, function=None):
    """Return a dict from the string encoding a field to export.
    The : is used as a separator to specify a target, if any.
    """
    name, sep, target = fld.partition(":")
    field_dict = {"name": name}
    if target:
        field_dict["target"] = target
    if function:
        field_dict["function"] = function
    return field_dict


def _convert_parser(parser):
    """Recursively process each list to replace encoded fields as string
    by dicts specifying each attribute by its relevant key.
    """
    result = []
    for line in parser:
        if isinstance(line, str):
            field_def = _convert_field(line)
        else:
            fld, sub = line
            if callable(sub) or isinstance(sub, str):
                field_def = _convert_field(fld, sub)
            else:
                field_def = (_convert_field(fld), _convert_parser(sub))
        result.append(field_def)
    return result
