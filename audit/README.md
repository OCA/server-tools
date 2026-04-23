# Audit module — technical documentation

This module provides a **generic audit/checklist engine** with a **dashboard-driven workflow** to:

- design an audit (domain → sections → questions),
- link the audit to auditable items (“targets”),
- conduct audits and store the result as immutable-ish “snapshots” (with scoring, comments, and optional images),
- browse results with search + pagination and a summary view.

The backend is standard Odoo ORM models; the UI entry point is an Odoo backend client action implemented in Owl/JS.

## Contents

- [Module summary](#module-summary)
- [Concepts](#concepts)
- [Data model](#data-model)
- [Security and access control](#security-and-access-control)
- [Audit lifecycle](#audit-lifecycle)
- [Scoring](#scoring)
- [UI / dashboard implementation](#ui--dashboard-implementation)
- [Backend API used by the dashboard](#backend-api-used-by-the-dashboard)
- [Configuration constants](#configuration-constants)
- [Operational notes and known constraints](#operational-notes-and-known-constraints)
- [Troubleshooting](#troubleshooting)

## Module summary

- **Module name**: `audit`
- **Location**: `src/internal_tools/audit/`
- **Manifest**: `src/internal_tools/audit/__manifest__.py`
- **Depends on**:
  - `base`
  - `web`
- **Backend assets**: all files under `audit/static/src/**/*` are included in `web.assets_backend`.

## Concepts

- **Domain** (`audit.domain`): a *type/class* of audit (e.g. “Retail Store H&S”, “Warehouse Safety”, “ISO 27001”).
- **Target** (`audit.target`): a *specific auditable item* within a domain (e.g. “Store #12”, “Warehouse Auckland”).
- **Section** (`audit.section`): groups questions within a domain (e.g. “Fire safety”, “Staff training”).
- **Question** (`audit.question`): a question template (prompt + answer type).
- **Inspector** (`audit.inspector`): the person conducting the audit (can be linked to `res.partner`).
- **Team** (`audit.team`): groups inspectors; leaders can see team members’ snapshots.
- **Snapshot** (`audit.snapshot`): a conducted audit instance for a target at a point in time.
- **Snapshot Section** (`audit.snapshot_section`): a copy of each section template stored on a snapshot.
- **Snapshot Question** (`audit.snapshot_question`): a copy of each question template stored on a snapshot, plus answers/comments/images.

## Data model

### `audit.domain` (Audit Domain)

- **Purpose**: defines an audit “template” boundary (sections, questions, and allowed targets).
- **Key fields**:
  - `name` (Text)
  - `section_ids` (One2many → `audit.section`)
  - `target_ids` (One2many → `audit.target` via `audit.target.domain_id`) — legacy/simple linkage
  - `target_rel_ids` (Many2many → `audit.target` via relation table `audit_domain_target_rel`) — primary linkage used by UI
  - `all_target_rel_ids` (computed/inverse Many2many) — merges `target_ids` + `target_rel_ids` for a unified UI field
  - **Key methods**:
  - `action_duplicate_domain()`: duplicates a domain and deep-copies sections + questions; links existing targets to the new domain.

### `audit.section` (Audit Section)

- **Purpose**: groups question templates under a domain.
- **Key fields**:
  - `name` (Text)
  - `domain_id` (Many2one → `audit.domain`, required)
  - `question_ids` (One2many → `audit.question`)

### `audit.question` (Audit Question Template)

- **Purpose**: defines a question prompt and its answer type.
- **Key fields**:
  - `prompt` (Text)
  - `answer_type` (Selection): `boolean` | `integer` | `float`
  - `section_id` (Many2one → `audit.section`, required)
  - `name` (computed from `prompt`) — used as the record display name

### `audit.target` (Auditable Target)

- **Purpose**: the entity being audited.
- **Key fields**:
  - `name` (Text)
  - `domain_id` (Many2one → `audit.domain`, optional)
  - `domain_rel_ids` (Many2many → `audit.domain` via `audit_domain_target_rel`)
  - `all_domain_rel_ids` (computed/inverse Many2many) — merges `domain_id` + `domain_rel_ids`
  - `snapshot_ids` (One2many → `audit.snapshot`)
  - **Key methods**:
  - `merge()`: consolidates targets with the same name by re-pointing snapshots and deleting duplicates.

### `audit.domain_target_rel` (Domain ↔ Target relation)

- **Purpose**: intermediate model/table used by the domain/target Many2many relationship.
- **Key fields**:
  - `domain_id` (Many2one → `audit.domain`, required)
  - `target_id` (Many2one → `audit.target`, required)

### `audit.inspector` (Inspector)

- **Purpose**: identifies the auditor/inspector/manager who conducts a snapshot.
- **Key fields**:
  - `name` (Char, required)
  - `partner_id` (Many2one → `res.partner`, optional)
  - `inspector_email` (related → `partner_id.email`, editable)
  - `forename`, `surname` (Char)
  - `active` (Boolean)
  - `snapshot_ids` (One2many → `audit.snapshot`)
  - `team_ids` (Many2many → `audit.team`)

### `audit.team` (Audit Team)

- **Purpose**: groups inspectors and defines leadership visibility.
- **Key fields**:
  - `name` (Char, required)
  - `team_member_ids` (Many2many → `audit.inspector`)
  - `team_leader_ids` (Many2many → `audit.inspector`)

### `audit.snapshot` (Audit Snapshot)

- **Purpose**: represents one conducted audit event for a target.
- **Key fields**:
  - `domain_id` (Many2one → `audit.domain`)
  - `target_id` (Many2one → `audit.target`, required)
  - `inspector_id` (Many2one → `audit.inspector`, required)
  - `date_conducted` (Datetime, default: now)
  - `snapshot_section_ids` (One2many → `audit.snapshot_section`, required)
  - `locked` (Boolean): UI uses this to prevent “submit” again; backend does not strictly enforce immutability
  - `active` (Boolean): used for archive/unarchive semantics
  - `percentage_score` (Float, computed): overall score in decimal form \(0.00–1.00\)
  - `questions_with_comments` (Integer, computed): count of snapshot questions with comments (computed only when locked)
  - `team_id` (Many2one → `audit.team`, optional)
  - **Creation behavior**:
  - `create()` is overridden to auto-generate `audit.snapshot_section` records for every `audit.section` in the chosen domain and `audit.snapshot_question` records for every `audit.question` in each section.

### `audit.snapshot_section` (Snapshot Section)

- **Purpose**: stores a copy of the domain’s section structure at the time of snapshot creation.
- **Key fields**:
  - `name` (Text)
  - `original_section_id` (Many2one → `audit.section`)
  - `domain_id` (Many2one → `audit.domain`, required)
  - `snapshot_id` (Many2one → `audit.snapshot`)
  - `snapshot_question_ids` (One2many → `audit.snapshot_question`)
  - `maximum_section_score`, `actual_section_score`, `percentage_section_score` (computed)

### `audit.snapshot_question` (Snapshot Question)

- **Purpose**: stores a copy of each question, plus answer/comment/image fields for the specific snapshot.
- **Key fields**:
  - `snapshot_id` (Many2one → `audit.snapshot`)
  - `snapshot_section_id` (Many2one → `audit.snapshot_section`, required)
  - `original_question_id` (Many2one → `audit.question`)
  - `prompt` (Text)
  - `answer_type` (Char)
  - Answer fields (only one is expected to be used per record):
    - `answer_yn` (Selection): `"0"`/`"1"`
    - `answer_star` (Selection): `"1"`..`"4"`
    - `answer_perc` (Float): \(0–100\)
  - `applicable` (Boolean, default `True`): excludes the question from snapshot maximum/actual scoring when `False`
  - `comment` (Text)
  - `image` (Image): can be set from the dashboard using a base64 data URL payload
  - `value` (Float, computed): normalized score used by snapshot scoring
  - **Key methods**:
  - `toggle_not_applicable(id)`: flips `applicable` and returns `{id, applicable}` (used by the dashboard)
  - `write(vals)`: if `image` is provided as `data:<mime>;base64,<payload>`, it strips the prefix and stores only the base64 payload.

## Security and access control

### Groups

- **Module category**: `Audit` (defined in `security/security.xml`)
- **Primary group**: `audit.group_audit_permission`
  - implies `base.group_user`
  - access rules are primarily done via standard model access and custom menu actions

### Model access

`security/ir.model.access.csv` grants full CRUD to `audit.group_audit_permission` for:

- `audit.domain`, `audit.section`, `audit.question`
- `audit.target`, `audit.domain_target_rel`
- `audit.inspector`, `audit.team`
- `audit.snapshot`, `audit.snapshot_section`, `audit.snapshot_question`
- `audit.menu.access.control` (Transient model used by server actions)

### Menu access control (server actions)

The menus for Teams/Inspectors/Snapshots/Snapshot Sections/Snapshot Questions are wired to **server actions** (`views/actions.xml`) that call methods on `audit.menu.access.control`.

Those methods return an `ir.actions.act_window` with a dynamic **domain**:

- **Admin users** (`base.group_system`): see everything.
- **Team leaders**: see records for inspectors in teams they lead.
- **Non-leaders**: see only their own records.

Important: this logic relies on an “inspector ↔ user” link. Parts of the implementation reference `audit.inspector.res_user_id`, which is not currently defined on `audit.inspector` in this module. See [Operational notes and known constraints](#operational-notes-and-known-constraints).

## Audit lifecycle

### 1) Design an audit (Domain → Sections → Questions)

- Create an `audit.domain`.
- Add `audit.section` records.
- Add `audit.question` records to each section, choosing an answer type:
  - boolean (Yes/No)
  - integer (1–4 stars)
  - float (0–100% slider)
- Optionally duplicate an existing domain via **Duplicate** on the domain form (deep-copies sections + questions).

### 2) Define auditable items (Targets)

- Create `audit.target` records.
- Link targets to domains using the `audit_domain_target_rel` relationship (exposed in the domain “Targets in Domain” page and target “Linked Domains” fields).

### 3) Set up inspectors and teams

- Create `audit.inspector` records (often linked to `res.partner` via `partner_id`).
- Create `audit.team` records and assign members/leaders.

### 4) Conduct an audit (create a Snapshot)

From **Audit Dashboard**:

- Select domain → target → inspector.
- Create the snapshot.

The snapshot creation process copies the current audit design into the snapshot:

- `audit.snapshot_section` rows are generated from `audit.section` rows for the domain.
- `audit.snapshot_question` rows are generated from `audit.question` rows for each section.

### 5) Answer questions (auto-save)

In the “View Questions” screen:

- Each question renders an input based on `answer_type`:
  - boolean → Yes/No dropdown
  - integer → star rating dropdown (1–4)
  - float → percentage slider (0–100)
- Comments are saved immediately when edited.
- Images can be uploaded; the dashboard sends a base64 data URL which the backend stores.
- A question can be toggled **Applicable / Excluded**; excluded questions are removed from overall snapshot scoring.

### 6) Submit the snapshot (lock)

Submitting a snapshot sets `audit.snapshot.locked = True`.

- The dashboard prevents double-submission and visually indicates locked snapshots.
- The backend does not strictly block edits to locked snapshots; “locked” is currently used as a workflow flag rather than a hard data integrity constraint.

### 7) View summary

For locked snapshots, the dashboard provides a Summary view that:

- groups questions by section,
- displays **only questions with comments**,
- displays any stored images,
- shows section scores and the overall snapshot score.

## Scoring

### Question-level score (`audit.snapshot_question.value`)

Snapshot questions normalize their answer into a value in the range \(0.0–1.0\).

Implementation (current):

- boolean:
  - `"1"` → \(1.0\)
  - `"0"` → \(0.0\)
- star rating:
  - `"1"`..`"4"` → \(\text{stars}/4\) → \(0.25..1.0\)
- percentage:
  - `0..100` → \(\text{percent}/100\) → \(0.0..1.0\)

Important: the compute currently adds all three components:

\[
value = float(answer\_yn) + \frac{float(answer\_star)}{4} + \frac{answer\_perc}{100}
\]

This works as intended **only if non-selected answer fields are empty-but-coercible to 0**, and only one answer input is used per question (as enforced by the UI).

### Snapshot overall score (`audit.snapshot.percentage_score`)

- **Maximum score**: counts **applicable** snapshot questions, with a weight of 1 per question.
- **Actual score**: sum of `value` for **applicable** snapshot questions.
- **Percentage score**: `round(actual_score / maximum_score, 2)` stored as a decimal \(0.00–1.00\).

The dashboard displays \(percentage\_score \times 100\%\).

### Pass/Fail threshold

- Backend constant: `PASS_THRESHOLD = 0.85`
- UI uses the same effective threshold (85%) when rendering PASS/FAIL in the snapshot list.

### Section scoring note

`audit.snapshot_section` computes per-section scores, but the current implementation does **not** exclude `applicable = False` questions from section maximum/actual computations. Overall snapshot scoring does exclude them.

## UI / dashboard implementation

### Entry point (menu → client action)

- Menu: `views/menus.xml` defines the top-level menu “Audit Dashboard”.
- Action: `views/actions.xml` registers an `ir.actions.client` with tag `audit.dashboard`.
- Client action: `static/src/javascript_components/dashboard/dashboard.js` registers the Owl component in the action registry.

### Components

- `AuditDashboard` (`dashboard.js`): router-like parent; switches between pages.
- `SnapshotList` (`snapshot_list.js`): table of searched snapshots; provides buttons to view questions and summary.
- `CreateSnapShot` (`create_snapshot.js`): selects domain/target/inspector and creates a snapshot.
- `Snapshot` (`snapshot.js`): renders sections/questions and implements auto-save + submission.
- `SnapshotSummary` (`snapshot_summary.js`): summary of commented questions and images for a locked snapshot.

### Shared store

`static/src/store.js` defines a reactive store used by the dashboard pages:

- Search inputs: `searchText`, `searchDate`, `searchStatus`, `searchPage`
- Results: `searchedSnapshots`, `numberOfPages`
- `executeSearch()` calls the backend `audit.snapshot.custom_search()`
- Pagination UI uses the store’s computed `visiblePages`

## Backend API used by the dashboard

The dashboard calls backend methods using the standard `orm` service (RPC to Odoo models).

### Snapshot search

- **Method**: `audit.snapshot.custom_search(search_string)`
- **Called by**: `store.executeSearch()`
- **Inputs**: `search_string` is JSON with keys:
  - `searchText` (string)
  - `searchDate` (string, date-like)
  - `searchStatus` (`PASS`/`FAIL`)
  - `searchPage` (int)
  - **Output**: dict:
  - `snapshots`: list of `search_read` dicts for `audit.snapshot`
  - `numberOfPages`: int
  - `newPageNumber`: int

### Snapshot creation

- **Method**: `audit.snapshot.create([vals])`
- **Called by**: `createSnapshotInstance()` in `dashboard_helpers.js`
- **Required fields** (enforced by backend override):
  - `domain_id`
  - `target_id`
  - `inspector_id`
- **Side effects**:
  - Generates snapshot sections + snapshot questions from the current domain template.

### Loading snapshot questions for display

The frontend typically loads questions by:

- reading the snapshot (for `snapshot_section_ids`),
- then `searchRead` on `audit.snapshot_question` for `snapshot_section_id in snapshot_section_ids`,
- then grouping by `snapshot_section_id[1]` (section display name).

For image thumbnails, the UI searches `ir.attachment` records for the `audit.snapshot_question.image` field and uses `/web/image/<attachment_id>` as a URL.

### Auto-save answers/comments/images

- **Method**: `audit.snapshot_question.write([id], {vals})`
- **Called by**: `autoSaveQuestionChanges()` in `dashboard_helpers.js`
- **Notes**:
  - if `vals.image` is a base64 data URL, backend `write()` strips the prefix before saving.

### Mark question not applicable

- **Method**: `audit.snapshot_question.toggle_not_applicable([id])`
- **Called by**: `questionApplicable()` in `dashboard_helpers.js`
- **Effect**: flips `applicable` and returns the new value.

### Submit snapshot (lock)

- **Method**: `audit.snapshot.write([snapshot_id], {vals: {locked: true}})`
- **Called by**: `submit()` in `dashboard_helpers.js`

## Configuration constants

In `models/audit_snapshot.py`:

- `PAGE_SIZE = 10`: number of snapshot rows per page returned by `custom_search()`
- `PASS_THRESHOLD = 0.85`: pass/fail cutoff used by `custom_search()` filtering and the list decorations

## Operational notes and known constraints

These are important when deploying or extending the module; they affect correctness and/or permissions.

- **Inspector ↔ User linking is incomplete**
  - Menu access control uses `audit.inspector.res_user_id`, but `audit.inspector` does not define `res_user_id` in this module.
  - Snapshot visibility in `audit.snapshot.snapshots_per_user()` tries to locate an inspector by either `res_user_id` or `partner_id`; only `partner_id` exists here.
  - Practical impact: non-admin users may see “no records” and/or menu actions may not filter as expected unless your deployment adds this link elsewhere.

- **Search fields are partially implemented**
  - The frontend submits `searchDate`, but the backend does not filter by date.
  - The backend attempts a `searchText` filter against a field named `search_text`, which is not defined on `audit.snapshot` in this module.

- **“Locked” is a workflow flag, not a hard constraint**
  - UI disables the submit button and indicates locking state.
  - Backend does not prevent `write()` on `audit.snapshot_question` (auto-save continues to work even if locked).

- **Section scoring differs from snapshot scoring**
  - Snapshot scoring excludes `applicable = False`.
  - Snapshot section scoring currently does not.

- **Uniqueness constraints**
  - Some models declare constraints using `models.Constraint(...)` instead of Odoo’s standard `_sql_constraints`. Depending on your Odoo version/config, the uniqueness guarantees described here may not be enforced at the database level.

## Extending the module

- **Add a new question answer type**
  - Backend:
    - update `audit.question.QUESTION_OPTIONS` in `models/audit_question.py`
    - add fields and scoring logic to `audit.snapshot_question` in `models/audit_snapshot.py`
  - Frontend:
    - update rendering and validation in `static/src/javascript_components/dashboard/snapshot.js`
    - update auto-save payload generation in `static/src/javascript_components/dashboard/dashboard_helpers.js`

- **Enforce immutability after submit**
  - Add backend guards in `audit.snapshot_question.write()` and/or `audit.snapshot.write()` to block edits when the parent snapshot is locked (except for admin/system users).

- **Make visibility rules robust**
  - Add an explicit link from `audit.inspector` to `res.users` (e.g. `res_user_id`) and standardize all access-control code to use the same link.


