# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2015-2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: C901

#####################################################################
#   library providing a function to analyse two progressive database
#   layouts from the OpenUpgrade server.
#####################################################################

import collections
import copy
from ast import literal_eval

try:
    from odoo.addons.openupgrade_scripts import apriori
except ImportError:
    from dataclasses import dataclass
    from dataclasses import field as dc_field

    @dataclass
    class NullApriori:
        renamed_modules: dict = dc_field(default_factory=dict)
        merged_modules: dict = dc_field(default_factory=dict)
        renamed_models: dict = dc_field(default_factory=dict)
        merged_models: dict = dc_field(default_factory=dict)

    apriori = NullApriori()


def module_map(module):
    return apriori.renamed_modules.get(
        module, apriori.merged_modules.get(module, module)
    )


def model_rename_map(model):
    return apriori.renamed_models.get(model, model)


def model_merge_map(model):
    return apriori.merged_models.get(model, model)


def model_map(model):
    return apriori.renamed_models.get(model, model_merge_map(model))


def inv_model_map(model):
    inv_model_map_dict = {v: k for k, v in apriori.renamed_models.items()}
    return inv_model_map_dict.get(model, model)


IGNORE_FIELDS = [
    "create_date",
    "create_uid",
    "id",
    "write_date",
    "write_uid",
]


def compare_records(dict_old, dict_new, fields):
    """
    Check equivalence of two OpenUpgrade field representations
    with respect to the keys in the 'fields' arguments.
    Take apriori knowledge into account for mapped modules or
    model names.
    Return True or False.
    """
    for field in fields:
        if field == "module":
            if module_map(dict_old["module"]) != dict_new["module"]:
                return False
        elif field == "model":
            if model_rename_map(dict_old["model"]) != dict_new["model"]:
                return False
        elif field == "relation":
            if model_map(dict_old["relation"]) != dict_new["relation"]:
                return False
        elif field == "other_prefix":
            if (
                dict_old["module"] != dict_old["prefix"]
                or dict_new["module"] != dict_new["prefix"]
            ):
                return False
            if dict_old["model"] == "ir.ui.view":
                # basically, to avoid the assets_backend case
                return False
        elif dict_old[field] != dict_new[field]:
            return False
    return True


def search(item, item_list, fields, get_all=None):
    """
    Find a match of a dictionary in a list of similar dictionaries
    with respect to the keys in the 'fields' arguments.
    Return the item if found or None.
    """
    all_found = []
    for other in item_list:
        if not compare_records(item, other, fields):
            continue
        if not get_all:
            return other
        if other["module"] != other["prefix"]:
            all_found.append(other)
    if get_all:
        return all_found
    # search for renamed fields
    if "field" in fields:
        for other in item_list:
            if not item["field"] or item["field"] is not None or item["isproperty"]:
                continue
            if compare_records(dict(item, field=other["field"]), other, fields):
                return other
    return None


def fieldprint(old, new, field, text, reprs):
    fieldrepr = "{}".format(old["field"])
    if old["field"] not in ("_inherits", "_order"):
        fieldrepr += " ({})".format(old["type"])
    fullrepr = "{:<12} / {:<24} / {:<30}".format(old["module"], old["model"], fieldrepr)
    if not text:
        text = f"{field} is now '{new[field]}' ('{old[field]}')"
        if field in ("column1", "column2"):
            text += f" [{old['table']}]"
        if field == "relation":
            text += " [nothing to do]"
        if field == "selection_keys":
            old_selection_keys = old.get("selection_keys") or ""
            new_selection_keys = new.get("selection_keys") or ""
            try:
                old_selection_keys = literal_eval(old_selection_keys)
                new_selection_keys = literal_eval(new_selection_keys)
            except Exception:  # pylint: disable=except-pass
                pass
            if isinstance(old_selection_keys, tuple | list) and isinstance(
                new_selection_keys, tuple | list
            ):
                removed = sorted(set(old_selection_keys) - set(new_selection_keys))
                added = sorted(set(new_selection_keys) - set(old_selection_keys))
                text = (
                    f"{field} {added and ('added: [' + ', '.join(added) + ']') or ''}"
                    f"{added and removed and ', ' or ''}"
                    f"{removed and ('removed: [' + ', '.join(removed) + ']') or ''}"
                )
                if added and not removed:
                    text += " (most likely nothing to do)"
    if field != "module":
        reprs[module_map(new["module"])].append(f"{fullrepr}: {text}")
    if field == "module":
        reprs[module_map(old["module"])].append(f"{fullrepr}: {text}")
        text = f"previously in module {old[field]}"
        fullrepr = "{:<12} / {:<24} / {:<30}".format(
            new["module"], old["model"], fieldrepr
        )
        reprs[module_map(new["module"])].append(f"{fullrepr}: {text}")


def report_generic(new, old, attrs, reprs):
    for attr in attrs:
        if attr == "required":
            if old[attr] != new["required"] and new["required"]:
                text = "now required"
                fieldprint(old, new, "", text, reprs)
        elif attr == "stored":
            if old[attr] != new[attr]:
                if new["stored"]:
                    if new.get("isproperty") and old.get("isproperty"):
                        text = "needs conversion to v18-style company dependent"
                    else:
                        text = "is now stored"
                else:
                    text = "not stored anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isfunction":
            if old[attr] != new[attr]:
                if new["isfunction"]:
                    text = "now a function"
                else:
                    text = "not a function anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isproperty":
            if old[attr] != new[attr]:
                if new[attr]:
                    text = "now a property"
                else:
                    text = "not a property anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isrelated":
            if old[attr] != new[attr]:
                if new[attr]:
                    text = "now related"
                else:
                    text = "not related anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "translate":
            if old[attr] != new[attr]:
                if new[attr]:
                    text = "now translatable"
                else:
                    text = "not translatable anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "table":
            if old[attr] != new[attr]:
                fieldprint(old, new, attr, "", reprs)
            if old[attr] and new[attr]:
                if old["column1"] != new["column1"]:
                    fieldprint(old, new, "column1", "", reprs)
                if old["column2"] != new["column2"]:
                    fieldprint(old, new, "column2", "", reprs)
        elif old[attr] != new[attr]:
            fieldprint(old, new, attr, "", reprs)


def compare_sets(old_records, new_records):
    """
    Compare a set of OpenUpgrade field representations.
    Try to match the equivalent fields in both sets.
    Return a textual representation of changes in a dictionary with
    module names as keys. Special case is the 'general' key
    which contains overall remarks and matching statistics.
    """
    reprs = collections.defaultdict(list)

    def clean_records(records):
        result = []
        for record in records:
            if record["field"] not in IGNORE_FIELDS:
                result.append(record)
        return result

    old_records = clean_records(old_records)
    new_records = clean_records(new_records)

    origlen = len(old_records)
    new_models = {column["model"] for column in new_records}
    old_models = {column["model"] for column in old_records}

    in_obsolete_models = 0

    obsolete_models = []
    for model in old_models:
        if model not in new_models:
            if model_map(model) not in new_models:
                obsolete_models.append(model)

    non_obsolete_old_records = []
    for column in copy.copy(old_records):
        if column["model"] in obsolete_models:
            in_obsolete_models += 1
        else:
            non_obsolete_old_records.append(column)

    def match(match_fields, report_fields, warn=False):
        count = 0
        for column in copy.copy(non_obsolete_old_records):
            found = search(column, new_records, match_fields)
            if found:
                if warn:
                    pass
                    # print "Tentatively"
                report_generic(found, column, report_fields, reprs)
                old_records.remove(column)
                non_obsolete_old_records.remove(column)
                new_records.remove(found)
                count += 1
        return count

    matched_direct = match(
        ["module", "mode", "model", "field", "type"],
        [
            "relation",
            "type",
            "selection_keys",
            "_inherits",
            "stored",
            "isfunction",
            "isrelated",
            "required",
            "table",
            "_order",
        ],
    )

    # same module, other type
    matched_other_type = match(
        ["module", "mode", "model", "field"],
        [
            "relation",
            "type",
            "selection_keys",
            "_inherits",
            "stored",
            "isfunction",
            "isrelated",
            "translate",
            "required",
            "table",
            "_order",
        ],
    )

    # other module, same type
    matched_other_module = match(
        ["mode", "model", "field", "type"],
        [
            "module",
            "relation",
            "selection_keys",
            "_inherits",
            "stored",
            "isfunction",
            "isrelated",
            "translate",
            "required",
            "table",
            "_order",
        ],
    )

    # same module, other type
    matched_other_type += match(
        ["module", "model", "field"],
        [
            "relation",
            "type",
            "selection_keys",
            "_inherits",
            "stored",
            "isfunction",
            "isrelated",
            "translate",
            "required",
            "table",
            "_order",
        ],
    )

    # other module, other type
    matched_other_module_other_type = match(
        ["mode", "model", "field"],
        [
            "module",
            "relation",
            "type",
            "selection_keys",
            "_inherits",
            "stored",
            "isfunction",
            "isrelated",
            "required",
            "table",
            "_order",
        ],
    )

    # Info that is displayed for deleted fields
    printkeys_old = [
        "relation",
        "required",
        "selection_keys",
        "_inherits",
        "mode",
        "attachment",
    ]
    # Info that is displayed for new fields
    printkeys_new = printkeys_old + [
        "hasdefault",
        "translate",
    ]
    for column in old_records:
        if column["field"] == "_order":
            continue
        # we do not care about removed non stored function/related fields
        if not column["stored"] and (column["isfunction"] or column["isrelated"]):
            continue
        if column["mode"] == "create":
            column["mode"] = ""
        printkeys = printkeys_old.copy()
        if not column["stored"] and not column["mode"]:
            printkeys.extend(["stored"])
        extra_message = ", ".join(
            [
                k + ": " + str(column[k] or False) if k != str(column[k]) else k
                for k in printkeys
                if k == "stored" or column[k]
            ]
        )
        if extra_message:
            extra_message = " " + extra_message
        fieldprint(column, column, "", "DEL" + extra_message, reprs)

    for column in new_records:
        if column["field"] == "_order":
            continue
        # we do not care about newly added non stored function/related fields
        if not column["stored"] and (column["isfunction"] or column["isrelated"]):
            continue
        if column["mode"] == "create":
            column["mode"] = ""
        printkeys = printkeys_new.copy()
        if column["isfunction"] or column["isrelated"]:
            printkeys.extend(["isfunction", "isrelated", "stored"])
        if not column["stored"] and not column["mode"]:
            printkeys.extend(["stored"])
        extra_message = ", ".join(
            [
                k + ": " + str(column[k] or False) if k != str(column[k]) else k
                for k in printkeys
                if k == "stored" or column[k]
            ]
        )
        if extra_message:
            extra_message = " " + extra_message
        fieldprint(column, column, "", "NEW" + extra_message, reprs)

    for line in [
        "# %d fields matched," % (origlen - len(old_records)),
        "# Direct match: %d" % matched_direct,
        "# Found in other module: %d" % matched_other_module,
        "# Found with different type: %d" % matched_other_type,
        "# Found in other module with different type: %d"
        % matched_other_module_other_type,
        "# In obsolete models: %d" % in_obsolete_models,
        "# Not matched: %d" % len(old_records),
        "# New columns: %d" % len(new_records),
    ]:
        reprs["general"].append(line)
    return reprs


def compare_xml_sets(old_records, new_records):
    reprs = collections.defaultdict(list)

    def match_updates(match_fields):
        old_updated, new_updated = {}, {}
        for column in copy.copy(old_records):
            found_all = search(column, old_records, match_fields, True)
            for found in found_all:
                old_records.remove(found)
        for column in copy.copy(new_records):
            found_all = search(column, new_records, match_fields, True)
            for found in found_all:
                new_records.remove(found)
        matched_records = list(old_updated.values()) + list(new_updated.values())
        matched_records = [y for x in matched_records for y in x]
        return matched_records

    def match(match_fields, match_type="direct"):
        matched_records = []
        for column in copy.copy(old_records):
            found = search(column, new_records, match_fields)
            if found:
                old_records.remove(column)
                new_records.remove(found)
                if match_type != "direct":
                    column["old"] = True
                    found["new"] = True
                    column[match_type] = found["module"]
                    found[match_type] = column["module"]
                found["domain"] = (
                    column["domain"] != found["domain"]
                    and column["domain"] != "[]"
                    and found["domain"] is False
                )
                column["domain"] = False
                found["definition"] = (
                    column["definition"]
                    and column["definition"] != found["definition"]
                    and "is now '{}' ('{}')".format(
                        found["definition"], column["definition"]
                    )
                )
                column["definition"] = False
                column["noupdate_switched"] = False
                found["noupdate_switched"] = column["noupdate"] != found["noupdate"]
                if match_type != "direct":
                    matched_records.append(column)
                    matched_records.append(found)
                elif (
                    match_type == "direct" and (found["domain"] or found["definition"])
                ) or found["noupdate_switched"]:
                    matched_records.append(found)
        return matched_records

    # direct match
    modified_records = match(["module", "model", "name"])

    # updated records (will be excluded)
    match_updates(["model", "name"])

    # other module, same full xmlid
    moved_records = match(["model", "name"], "moved")

    # other module, same suffix, other prefix
    renamed_records = match(["model", "suffix", "other_prefix"], "renamed")

    for record in old_records:
        record["old"] = True
        record["domain"] = False
        record["definition"] = False
        record["noupdate_switched"] = False
    for record in new_records:
        record["new"] = True
        record["domain"] = False
        record["definition"] = False
        record["noupdate_switched"] = False

    sorted_records = sorted(
        old_records + new_records + moved_records + renamed_records + modified_records,
        key=lambda k: (k["model"], "old" in k, k["name"]),
    )
    for entry in sorted_records:
        content = ""
        if "old" in entry:
            content = f"DEL {entry['model']}: {entry['name']}"
            if "moved" in entry:
                content += f" [moved to {entry['moved']} module]"
            elif "renamed" in entry:
                content += f" [renamed to {entry['renamed']} module]"
        elif "new" in entry:
            content = f"NEW {entry['model']}: {entry['name']}"
            if "moved" in entry:
                content += f" [moved from {entry['moved']} module]"
            elif "renamed" in entry:
                content += f" [renamed from {entry['renamed']} module]"
        if "old" not in entry and "new" not in entry:
            content = f"{entry['model']}: {entry['name']}"
        if entry["domain"]:
            content += " (deleted domain)"
        if entry["definition"]:
            content += f" (changed definition: {entry['definition']})"
        if entry["noupdate"]:
            content += " (noupdate)"
        if entry["noupdate_switched"]:
            content += " (noupdate switched)"
        reprs[module_map(entry["module"])].append(content)
    return reprs


def compare_model_sets(old_records, new_records):
    """
    Compare a set of OpenUpgrade model representations.
    """
    reprs = collections.defaultdict(list)

    new_models = {column["model"]: column["module"] for column in new_records}
    old_models = {column["model"]: column["module"] for column in old_records}

    obsolete_models = []
    for column in copy.copy(old_records):
        model = column["model"]
        if model in old_models:
            if model not in new_models:
                if model_map(model) not in new_models:
                    obsolete_models.append(model)
                    text = f"obsolete model {model}"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[module_map(column["module"])].append(text)
                    reprs["general"].append(
                        f"obsolete model {model} "
                        f"[module {module_map(column['module'])}]"
                    )
                elif model_merge_map(model) in new_models:
                    text = f"obsolete model {model} (merged to {model_map(model)})"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[module_map(column["module"])].append(text)
                    reprs["general"].append(
                        f"obsolete model {model} (merged to {model_map(model)}) "
                        f"[module {module_map(column['module'])}]"
                    )
                else:
                    moved_module = ""
                    if module_map(column["module"]) != new_models[model_map(model)]:
                        moved_module = f" in module {new_models[model_map(model)]}"
                    text = (
                        f"obsolete model {model}"
                        f" (renamed to {model_map(model)}{moved_module})"
                    )
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[module_map(column["module"])].append(text)
                    reprs["general"].append(
                        f"obsolete model {model} (renamed to {model_map(model)}) "
                        f"[module {module_map(column['module'])}]"
                    )
            else:
                if module_map(column["module"]) != new_models[model]:
                    text = f"model {model} (moved to {new_models[model]})"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[module_map(column["module"])].append(text)
                    text = f"model {model} (moved from {old_models[model]})"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"

    for column in copy.copy(new_records):
        model = column["model"]
        if model in new_models:
            if model not in old_models:
                if inv_model_map(model) not in old_models:
                    text = f"new model {model}"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[column["module"]].append(text)
                    reprs["general"].append(
                        "new model {} [module {}]".format(model, column["module"])
                    )
                else:
                    moved_module = ""
                    if column["module"] != module_map(old_models[inv_model_map(model)]):
                        moved_module = f" in module {old_models[inv_model_map(model)]}"
                    text = (
                        f"new model {model} "
                        f"(renamed from {inv_model_map(model)}{moved_module})"
                    )
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[column["module"]].append(text)
                    reprs["general"].append(
                        f"new model {model} (renamed from {inv_model_map(model)}) "
                        f"[module {column['module']}]"
                    )
            else:
                if column["module"] != module_map(old_models[model]):
                    text = f"model {model} (moved from {old_models[model]})"
                    if column["model_type"]:
                        text += f" [{column['model_type']}]"
                    reprs[column["module"]].append(text)
    return reprs
