import {fonts} from "@html_editor/utils/fonts";
import {patch} from "@web/core/utils/patch";

patch(fonts, {
    /**
     * Updated parser for FontAwesome >= 6.7.2 icons.
     * Matches icon classes like .fa-icon-name
     */
    fontIcons: [{base: "fa", parser: /\.(fa-(?:\w|-)+)/i}],

    /**
     * Check if a CSS rule is a valid FontAwesome rule.
     * @param {String} selectorText - The CSS selector text
     * @param {String} cssText - The CSS rule text
     * @returns {Boolean} True if the rule defines the --fa variable
     */
    _isValidFontAwesomeRule(selectorText, cssText) {
        return selectorText && cssText && cssText.includes("--fa:");
    },

    /**
     * Processes CSS rule selectors by filtering and grouping them based on a regex pattern.
     *
     * @private
     * @param {String} selectorText - The CSS selector text containing one or more comma-separated selectors.
     * @param {String} cssText - The full CSS rule text including curly braces and properties.
     * @param {RegExp} filter - A regular expression to match and extract relevant selectors.
     *                          The first capture group should contain the name to extract.
     * @returns {Object|null} An object containing the processed selector data, or null if no matches found.
     * @returns {String} returns.selector - The matched selectors joined by commas.
     * @returns {String} returns.css - The CSS properties without the surrounding braces.
     * @returns {String[]} returns.names - An array of extracted names from the first capture group of the filter regex.
     */
    _processRuleSelectors(selectorText, cssText, filter) {
        const selectors = selectorText.split(/\s*,\s*/);
        let data = null;
        for (let s = 0; s < selectors.length; s++) {
            const match = selectors[s].trim().match(filter);
            if (!match) {
                continue;
            }
            if (data) {
                data.selector += ", " + match[0];
                data.names.push(match[1]);
            } else {
                data = {
                    selector: match[0],
                    css: cssText.replace(/(^.*\{\s*)|(\s*\}\s*$)/g, ""),
                    names: [match[1]],
                };
            }
        }
        return data;
    },

    /**
     * Override getCssSelectors to only process rules that define the --fa variable
     * (for FontAwesome >= 6.7.2 compatibility)
     * @param {RegExp} filter
     * @returns {Object[]} Array of CSS rules descriptions (objects). A rule is
     *          defined by 3 values: 'selector', 'css' and 'names'. 'selector'
     *          is a string which contains the whole selector, 'css' is a string
     *          which contains the css properties and 'names' is an array of the
     *          first captured groups for each selector part. E.g.: if the
     *          filter is set to match .fa-* rules and capture the icon names,
     *          the rule:
     *              '.fa-alias1::before, .fa-alias2::before { hello: world; }'
     *          will be retrieved as
     *              {
     *                  selector: '.fa-alias1::before, .fa-alias2::before',
     *                  css: 'hello: world;',
     *                  names: ['.fa-alias1', '.fa-alias2'],
     *              }
     */
    getCssSelectors(filter) {
        if (this.cacheCssSelectors[filter]) {
            return this.cacheCssSelectors[filter];
        }
        this.cacheCssSelectors[filter] = [];
        const seenUnicodes = new Set();
        // eslint-disable-next-line no-undef
        const sheets = document.styleSheets;
        for (let i = 0; i < sheets.length; i++) {
            let rules = null;
            try {
                // Try...catch because Firefox not able to enumerate
                // document.styleSheets[].cssRules[] for cross-domain
                // stylesheets.
                rules = sheets[i].rules || sheets[i].cssRules;
            } catch {
                continue;
            }
            if (!rules) {
                continue;
            }

            for (let r = 0; r < rules.length; r++) {
                const selectorText = rules[r].selectorText;
                const cssText = rules[r].cssText;
                // Only process rules that define the --fa variable (for FontAwesome >= 6.7.2)
                if (!this._isValidFontAwesomeRule(selectorText, cssText)) {
                    continue;
                }
                // Extract unicode value and skip if duplicate
                const unicodeMatch = cssText.match(/--fa:\s*["']\\([^"']+)["']/);
                if (unicodeMatch && seenUnicodes.has(unicodeMatch[1])) {
                    continue;
                }
                if (unicodeMatch) {
                    seenUnicodes.add(unicodeMatch[1]);
                }
                const data = this._processRuleSelectors(selectorText, cssText, filter);
                if (data) {
                    this.cacheCssSelectors[filter].push(data);
                }
            }
        }
        return this.cacheCssSelectors[filter];
    },
});
