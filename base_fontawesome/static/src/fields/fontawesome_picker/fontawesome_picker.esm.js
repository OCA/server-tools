/** @odoo-module **/

import {Component, onWillStart, useRef, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useAutofocus} from "@web/core/utils/hooks";
import {usePopover} from "@web/core/popover/popover_hook";

// Catalog is read from the v4-shims stylesheet (".fa.fa-<name>" selectors), NOT
// from all.css (".fa-<name>::before"). Reason: a bare "fa" prefix resolves to
// Free Solid in FontAwesome 6, so storing "fa fa-x" only renders for icons that
// the v4-shims layer maps to the right font-family/weight per name (solid,
// regular and brand alike). The full all.css catalog also contains FA6-only
// brand/regular icons that would be saved as "fa fa-x" and render blank. The
// v4-shims set is exactly the icons that render with the universal "fa fa-x"
// class in every bundle (backend, PoS, reports), which is what this widget
// writes. We parse it locally instead of depending on web_editor (whose
// computeFonts() caches globally through a pollutable lodash _.once wrapper).
const FA_SHIM_SELECTOR_PARSER = /\.fa\.(fa-[\w-]+)/i;

// Session-level memo: the loaded catalog does not change within a page session.
// Unlike web_editor's global _.once on a shared object, this only ever holds the
// result of this function, so it cannot be polluted by other code. Only a
// non-empty result is cached, so an early (pre-CSS) read is never frozen in.
let _iconsCache = null;

/**
 * Collect the FontAwesome icon class names declared in the loaded stylesheets.
 *
 * Reads document.styleSheets at call time (not at module load) so it runs after
 * base_fontawesome's CSS bundle has been applied. Returns the deduplicated,
 * alphabetically sorted list of v4-shims "fa-*" names (those that render with a
 * bare "fa" prefix).
 *
 * @returns {String[]}
 */
function collectFontAwesomeIcons() {
    if (_iconsCache) {
        return _iconsCache;
    }
    const names = new Set();
    for (const sheet of document.styleSheets) {
        let rules = null;
        try {
            rules = sheet.rules || sheet.cssRules;
        } catch {
            // Cross-origin stylesheets throw when their rules are accessed.
            // FontAwesome is served locally, so this only skips unrelated sheets.
            continue;
        }
        if (!rules) {
            continue;
        }
        for (const rule of rules) {
            if (!rule.selectorText) {
                continue;
            }
            for (const selector of rule.selectorText.split(/\s*,\s*/)) {
                const match = selector.trim().match(FA_SHIM_SELECTOR_PARSER);
                if (match) {
                    names.add(match[1]);
                }
            }
        }
    }
    const icons = [...names].sort();
    if (icons.length) {
        _iconsCache = icons;
    }
    return icons;
}

/**
 * Popover content: a search box and the grid of icons. Rendered through the
 * popover service so it floats in the viewport (auto-flipped, single scroll)
 * instead of growing the form's scroll height.
 */
export class FontAwesomePickerGrid extends Component {
    setup() {
        this.state = useState({search: ""});
        // The popover service does not move focus; focus the search box on open.
        useAutofocus();
    }

    get matchedIcons() {
        const search = this.state.search.trim().toLowerCase();
        if (!search) {
            return this.props.icons;
        }
        return this.props.icons.filter((name) => name.includes(search));
    }

    // Cap the rendered icons: the full FontAwesome catalog is ~2000 entries, and
    // rendering them all at once on open is needlessly heavy. The search narrows
    // the list, and `hasMore` hints the user to refine when the cap is hit.
    get visibleIcons() {
        return this.matchedIcons.slice(0, this.constructor.MAX_RESULTS);
    }

    get hasMore() {
        return this.matchedIcons.length > this.constructor.MAX_RESULTS;
    }

    get searchPlaceholder() {
        return _t("Search icon...");
    }

    get emptyLabel() {
        return _t("No FontAwesome icons available.");
    }

    get moreLabel() {
        return _t("Refine your search to narrow the list.");
    }

    onSelect(name) {
        this.props.onSelect(name);
        this.props.close();
    }
}

FontAwesomePickerGrid.MAX_RESULTS = 300;
FontAwesomePickerGrid.template = "base_fontawesome.FontAwesomePickerGrid";
FontAwesomePickerGrid.props = {
    icons: {type: Array},
    empty: {type: Boolean},
    onSelect: {type: Function},
    // Injected by the popover service to dismiss the popover.
    close: {type: Function, optional: true},
};

export class FontAwesomePicker extends Component {
    setup() {
        this.toggleRef = useRef("toggle");
        this.popover = usePopover();
        this.closePopover = null;
        this.icons = [];
        this.empty = false;
        onWillStart(() => {
            // Lazy read: the CSS bundle is guaranteed applied by now.
            this.icons = collectFontAwesomeIcons();
            this.empty = this.icons.length === 0;
            if (this.empty) {
                // eslint-disable-next-line no-console
                console.warn(
                    "FontAwesomePicker: no FontAwesome icons found in the loaded " +
                        "stylesheets; is base_fontawesome installed?"
                );
            }
        });
    }

    togglePopover() {
        if (this.closePopover) {
            this.closePopover();
            this.closePopover = null;
            return;
        }
        this.closePopover = this.popover.add(
            this.toggleRef.el,
            FontAwesomePickerGrid,
            {
                icons: this.icons,
                empty: this.empty,
                onSelect: (name) => this.selectIcon(name),
            },
            {
                position: "bottom",
                popoverClass: "o_fa_picker_popover",
                onClose: () => {
                    this.closePopover = null;
                },
            }
        );
    }

    get placeholderLabel() {
        return _t("Select an icon");
    }

    get clearLabel() {
        return _t("Clear");
    }

    selectIcon(name) {
        // Store the full class ("fa fa-x") so the value renders directly through
        // <i t-att-class/>, matching the existing convention of icon fields.
        this.props.update(`fa ${name}`);
    }

    clear() {
        // Empty string is the canonical empty value for a Char field.
        this.props.update("");
    }
}

FontAwesomePicker.template = "base_fontawesome.FontAwesomePicker";
FontAwesomePicker.components = {FontAwesomePickerGrid};
// `update` is optional in standardFieldProps, but this widget cannot work without
// it (selecting/clearing an icon writes through it), so require it explicitly.
FontAwesomePicker.props = {
    ...standardFieldProps,
    update: {type: Function},
};
FontAwesomePicker.supportedTypes = ["char"];

// Registered only on the base "fields" registry (form views). List/tree support
// is intentionally out of scope to avoid dropdown overflow inside table cells.
registry.category("fields").add("fontawesome_picker", FontAwesomePicker);
