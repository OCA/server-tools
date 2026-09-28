/** @odoo-module **/
/* global QUnit */

import {click, editInput, getFixture, mount} from "@web/../tests/helpers/utils";
import {makeView, setupViewRegistries} from "@web/../tests/views/helpers";
import {FontAwesomePickerGrid} from "@base_fontawesome/fields/fontawesome_picker/fontawesome_picker.esm";
import {makeTestEnv} from "@web/../tests/helpers/mock_env";

// The field reads its catalog from the loaded v4-shims stylesheet
// (".fa.fa-<name>" selectors). QUnit runs headless, so we inject a deterministic
// set of such rules, including a brand (fa-facebook) to prove brand icons are
// offered and stored with the universal "fa" prefix.
const FA_TEST_ICONS = [
    "fa-facebook",
    "fa-search",
    "fa-shopping-cart",
    "fa-star",
    "fa-undo",
];
let styleEl = null;
let serverData = null;
let target = null;

QUnit.module("base_fontawesome", (hooks) => {
    hooks.before(() => {
        styleEl = document.createElement("style");
        styleEl.textContent = FA_TEST_ICONS.map(
            (name) => `.fa.${name}:before { content: "x"; }`
        ).join("\n");
        document.head.appendChild(styleEl);
    });

    hooks.after(() => {
        styleEl.remove();
    });

    hooks.beforeEach(() => {
        target = getFixture();
        serverData = {
            models: {
                partner: {
                    fields: {
                        icon: {string: "Icon", type: "char", searchable: true},
                    },
                    records: [
                        {id: 1, icon: "fa fa-undo"},
                        {id: 2, icon: false},
                    ],
                },
            },
        };
        setupViewRegistries();
    });

    // --- Grid component in isolation (deterministic, controlled catalog) ---

    QUnit.module("FontAwesomePickerGrid");

    QUnit.test("lists every icon and filters by search (V1, V2)", async (assert) => {
        const env = await makeTestEnv();
        await mount(FontAwesomePickerGrid, target, {
            env,
            props: {
                icons: FA_TEST_ICONS,
                empty: false,
                onSelect: () => undefined,
                close: () => undefined,
            },
        });
        assert.containsN(target, ".o_fa_picker_item", FA_TEST_ICONS.length);
        await editInput(target, ".o_fa_picker_search", "shopping");
        assert.containsOnce(target, ".o_fa_picker_item");
        assert.strictEqual(
            target.querySelector(".o_fa_picker_item").title,
            "fa-shopping-cart"
        );
    });

    QUnit.test("selecting an icon notifies and closes (V3)", async (assert) => {
        const env = await makeTestEnv();
        const selected = [];
        let closed = false;
        await mount(FontAwesomePickerGrid, target, {
            env,
            props: {
                icons: FA_TEST_ICONS,
                empty: false,
                onSelect: (name) => selected.push(name),
                close: () => {
                    closed = true;
                },
            },
        });
        await click(target, ".o_fa_picker_item[title='fa-undo']");
        assert.deepEqual(selected, ["fa-undo"]);
        assert.ok(closed, "the popover close was requested");
    });

    QUnit.test("empty catalog shows a message (R2)", async (assert) => {
        const env = await makeTestEnv();
        await mount(FontAwesomePickerGrid, target, {
            env,
            props: {
                icons: [],
                empty: true,
                onSelect: () => undefined,
                close: () => undefined,
            },
        });
        assert.containsNone(target, ".o_fa_picker_item");
        assert.containsOnce(target, ".o_fa_picker_empty");
    });

    QUnit.test(
        "a search with no match shows neither items nor empty notice",
        async (assert) => {
            const env = await makeTestEnv();
            await mount(FontAwesomePickerGrid, target, {
                env,
                props: {
                    icons: FA_TEST_ICONS,
                    empty: false,
                    onSelect: () => undefined,
                    close: () => undefined,
                },
            });
            await editInput(target, ".o_fa_picker_search", "zzz-nope");
            // No item matches, but this is "filtered to zero", not "empty catalog":
            // the empty-catalog notice must NOT appear (different XML branch).
            assert.containsNone(target, ".o_fa_picker_item");
            assert.containsNone(target, ".o_fa_picker_empty");
        }
    );

    QUnit.test("the rendered grid is capped and hints to refine", async (assert) => {
        const env = await makeTestEnv();
        const many = Array.from(
            {length: FontAwesomePickerGrid.MAX_RESULTS + 50},
            (unused, i) => `fa-gen-${i}`
        );
        await mount(FontAwesomePickerGrid, target, {
            env,
            props: {
                icons: many,
                empty: false,
                onSelect: () => undefined,
                close: () => undefined,
            },
        });
        assert.containsN(
            target,
            ".o_fa_picker_item",
            FontAwesomePickerGrid.MAX_RESULTS
        );
        assert.containsOnce(target, ".o_fa_picker_more");
    });

    // --- Field widget through a form view ---

    QUnit.module("FontAwesomePicker");

    QUnit.test("shows a preview and clears the value (V1, V3)", async (assert) => {
        await makeView({
            type: "form",
            resModel: "partner",
            resId: 1,
            serverData,
            arch: `<form><field name="icon" widget="fontawesome_picker"/></form>`,
        });
        assert.containsOnce(target, ".o_fa_picker_toggle i.fa.fa-undo");
        assert.containsOnce(target, ".o_fa_picker_clear");
        await click(target, ".o_fa_picker_clear");
        assert.containsNone(target, ".o_fa_picker_clear");
        assert.strictEqual(
            target.querySelector(".o_fa_picker_toggle span").textContent.trim(),
            "Select an icon"
        );
    });

    QUnit.test(
        "opening the picker writes the chosen class, including brands (V1, V3, V5)",
        async (assert) => {
            await makeView({
                type: "form",
                resModel: "partner",
                resId: 2,
                serverData,
                arch: `<form><field name="icon" widget="fontawesome_picker"/></form>`,
            });
            assert.containsNone(target, ".o_fa_picker_popover");
            await click(target, ".o_fa_picker_toggle");
            assert.containsOnce(target, ".o_fa_picker_popover");
            // Catalog is read from the loaded v4-shims stylesheet, not hard-coded;
            // brand icons are offered and stored with the universal "fa" prefix
            // (v4-shims maps "fa fa-<brand>" to the brands font, so it renders).
            assert.containsOnce(target, ".o_fa_picker_item[title='fa-facebook']");
            await click(target, ".o_fa_picker_item[title='fa-facebook']");
            assert.containsNone(
                target,
                ".o_fa_picker_popover",
                "popover closes on select"
            );
            assert.strictEqual(
                target.querySelector(".o_fa_picker_toggle span").textContent.trim(),
                "fa fa-facebook"
            );
        }
    );

    QUnit.test("a second click on the toggle closes the popover", async (assert) => {
        await makeView({
            type: "form",
            resModel: "partner",
            resId: 2,
            serverData,
            arch: `<form><field name="icon" widget="fontawesome_picker"/></form>`,
        });
        await click(target, ".o_fa_picker_toggle");
        assert.containsOnce(target, ".o_fa_picker_popover");
        await click(target, ".o_fa_picker_toggle");
        assert.containsNone(target, ".o_fa_picker_popover", "toggling again closes it");
    });

    QUnit.test(
        "an empty value shows the placeholder and no clear button",
        async (assert) => {
            await makeView({
                type: "form",
                resModel: "partner",
                resId: 2,
                serverData,
                arch: `<form><field name="icon" widget="fontawesome_picker"/></form>`,
            });
            assert.containsNone(target, ".o_fa_picker_clear");
            assert.strictEqual(
                target.querySelector(".o_fa_picker_toggle span").textContent.trim(),
                "Select an icon"
            );
        }
    );

    QUnit.test("readonly renders the icon without a toggle (V4)", async (assert) => {
        await makeView({
            type: "form",
            resModel: "partner",
            resId: 1,
            serverData,
            arch: `<form><field name="icon" widget="fontawesome_picker" readonly="1"/></form>`,
        });
        assert.containsOnce(target, ".o_fa_picker_readonly i.fa.fa-undo");
        assert.containsNone(target, ".o_fa_picker_toggle");
    });
});
