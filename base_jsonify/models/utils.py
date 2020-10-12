def convert_simple_to_full_parser(parser):
    """Convert a simple API style parser to a full parser"""
    assert isinstance(parser, list)
    return {"fields": _convert_parser(parser)}


def _f(f, function=None):
    """Return a dict from the string encoding a field to export.
    The : is used as a separator to specify a target, if any.
    """
    field_split = f.split(":")
    field_dict = {"name": field_split[0]}
    if len(field_split) > 1:
        field_dict["target"] = field_split[1]
    if function:
        field_dict["function"] = function
    return field_dict


def _convert_parser(parser):
    """Recursively process each list to replace encoding fields as string
    by dicts specifying each attribute by its relevant key.
    """
    result = []
    for line in parser:
        if isinstance(line, str):
            result.append(_f(line))
        else:
            f, sub = line
            if callable(sub) or isinstance(sub, str):
                result.append(_f(f, sub))
            else:
                result.append((_f(f), _convert_parser(sub)))
    return result
