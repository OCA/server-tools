/** @odoo-module **/
import {Component, useState, xml} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {store} from "../../store";

/**
 * This method runs when we click "View Questions" so we can load all the sections and questions
 * for the snapshot being viewed.
 * @param {*} data
 * @param {*} api
 * @returns
 */
export async function orderCurrentSnapshotInstanceData(data, api) {
    const sectionsAndQuestions = [];

    const sectionIDs = data[0]
        ? data[0].snapshot_section_ids
        : data.snapshot_section_ids;
    // Find updated associated snapshot_questions for each snapshot_section_id
    const questions = await api.orm.searchRead(
        "audit.snapshot_question",
        [["snapshot_section_id", "in", sectionIDs]],
        []
    );

    // Fetch any attachments as necessary
    const questionIds = questions.map((question) => question.id);
    const attachments = await api.orm.searchRead(
        "ir.attachment",
        [
            ["res_id", "in", questionIds],
            ["res_model", "=", "audit.snapshot_question"],
            ["res_field", "=", "image"],
        ],
        // Exclude binary data fields
        ["id", "res_id", "res_model", "res_field", "name", "mimetype", "file_size"]
    );
    // Add number, and join attachments
    questions.forEach((question) => {
        question.number = question.id;
        question.img_src = null;
        attachments.forEach((attachment) => {
            if (attachment.res_id === question.id) {
                // Construct the image URL using the attachment ID instead of binary data
                question.img_src = `/web/image/${attachment.id}`;
            }
        });
    });
    let snapshotSectionNames = questions.map((entry) => entry.snapshot_section_id[1]);
    snapshotSectionNames = snapshotSectionNames.filter(
        (value, index) => snapshotSectionNames.indexOf(value) === index
    );

    // For each snapshot_section_name we want the questions belonging to it
    let snapshotSectionQuestions = [];
    for (const sectionName of snapshotSectionNames) {
        for (const question of questions) {
            if (question.snapshot_section_id[1] === sectionName) {
                snapshotSectionQuestions.push(question);
            }
        }
        sectionsAndQuestions.push({
            snapshot_section_name: sectionName,
            questions: snapshotSectionQuestions,
            locked: data[0] ? data[0].locked : data.locked,
            snapshot_id: data[0] ? data[0].id : data.id,
        });
        snapshotSectionQuestions = [];
    }
    return sectionsAndQuestions;
}

/**
 * This method runs when we click "Answer Questions", it will call the ORM, audit.snapshot class,
 * which will create a new Snapshot Instance.
 * @param {*} data
 * @param {*} api
 * @returns
 */
export async function createSnapshotInstance(data, api) {
    try {
        const orm = api.orm;
        const [snapshotId] = await orm.create("audit.snapshot", [data]);

        // Validate response
        if (!snapshotId) {
            throw new Error("Failed to create snapshot (no ID returned)");
        }

        // Fetch newly created Snapshot
        const snapshot = await orm.searchRead(
            "audit.snapshot",
            [["id", "=", snapshotId]],
            []
        );

        // Validate snapshot
        if (!snapshot || snapshot.length === 0) {
            throw new Error(
                `Created snapshot not found in database with ID: ${snapshotId}`
            );
        }
        return await orderCurrentSnapshotInstanceData(snapshot, api);
    } catch (error) {
        console.error(
            "dashboard_helpers.js::createSnapshotInstance > Error creating snapshot:",
            error
        );
        throw error;
    }
}

/**
 * Call the audit.snapshot class's `write` function to update a specific Snapshot instance
 * @param {*} sectionsWithQuestions
 * @param {*} submitSnapshot
 * @param {*} api
 * @returns
 */
export async function submit(sectionsWithQuestions, submitSnapshot, api) {
    // If this is a submit request, first lock the snapshot
    if (submitSnapshot) {
        await api.orm.call(
            "audit.snapshot",
            "write",
            [sectionsWithQuestions[0].snapshot_id],
            {
                vals: {locked: true},
            }
        );
        return true;
    }
    return false;
}

/**
 * Call toggle_not_applicable from the audit.snapshot class to mark a snapshot question
 * as not applicable.
 * @param {*} question
 * @param {*} api
 * @returns
 */
export async function questionApplicable(question, api) {
    const result = await api.orm.call(
        "audit.snapshot_question",
        "toggle_not_applicable",
        [question.id],
        {}
    );
    question.applicable = result.applicable;
}

/**
 * Retrieve all Snapshot records from the database.
 * @param {*} api
 * @returns
 */
export async function allSnapshotInstances(api) {
    return api.orm.searchRead("audit.snapshot", [], []);
}

/**
 * Load the SnapshotQuestions for each SnapshotSection.
 * @param {*} section_ids
 * @param api
 * @returns
 */
export async function getSectionSnapshotQuestions(section_ids, api) {
    const questions = {};
    for (const sectionId of section_ids) {
        const section_id_questions = await api.orm.searchRead(
            "audit.snapshot_question",
            [["snapshot_section_id", "=", sectionId]],
            []
        );

        if (section_id_questions) {
            questions[sectionId] = section_id_questions;
        }
    }
    return questions;
}

/**
 * For each snapshot, retrieve its Snapshot Sections, then for each Snapshot Section,
 * retrieve its Snapshot Questions.  Bundle it all together and return the result.
 * @param {*} allSnapshots
 * @param api
 * @returns
 */
export async function prepareAllSnapshotQuestions(allSnapshots, api) {
    for (const snapshot of allSnapshots) {
        const sectionIds = snapshot.snapshot_section_ids;
        const questions = await getSectionSnapshotQuestions(sectionIds, api);
        Object.assign(snapshot, {questions});
    }
    return allSnapshots;
}

/**
 * `readAsDataURL()` produces `data:<mime>;base64,<payload>`. Odoo `Image` fields expect
 * a plain base64 string; the server rejects a full data URL.
 * @param {string|boolean|undefined} value
 * @returns {string|boolean|undefined}
 */
function imageValueForOdooWrite(value) {
    if (!value || typeof value !== "string" || !value.startsWith("data:")) {
        return value;
    }
    const marker = ";base64,";
    const index = value.indexOf(marker);
    if (index === -1) {
        return value;
    }
    return value.slice(index + marker.length);
}

/**
 * Whenever any part of a Snapshot Question changes or is updated, the change is immediately saved.
 * The purpose of this function is to take care of auto saving Snapshot Questions.
 * @param {*} question
 * @param {*} image
 * @param {*} api
 */
export function autoSaveQuestionChanges(question, image, api) {
    // We will update a snapshot whether it is locked or not - Sam's request
    api.orm
        .searchRead(
            "audit.snapshot",
            [["snapshot_section_ids", "in", question.snapshot_section_id[0]]],
            []
        )
        .then(() => {
            let new_values = {};
            // Have to do a fresh lookup of the question because we don't know if the internal `save` has been called on it
            api.orm
                .searchRead("audit.snapshot_question", [["id", "=", question.id]], [])
                .then((rows) => {
                    const row = rows[0];
                    if (question.comment === row.comment) {
                        // eslint-disable-next-line no-self-assign
                        question.comment = question.comment;
                    } else if (
                        question.comment &&
                        row.comment &&
                        question.comment !== row.comment
                    ) {
                        question.comment = row.comment;
                    }
                    question.image = row.image;

                    new_values = {
                        comment: question.comment,
                        answer_yn: question.answer_yn,
                        answer_star: question.answer_star,
                        answer_perc: question.answer_perc,
                        image: image
                            ? imageValueForOdooWrite(image)
                            : question.image,
                    };

                    api.orm.call("audit.snapshot_question", "write", [question.id], {
                        vals: new_values,
                    });
                });
        });
}

export class PageComponent extends Component {
    static template = xml`
    <nav aria-label="Page navigation">
      <ul class="pagination justify-content-center snapshot-pagination">

        <!-- 'Previous' page Button-->
        <li t-attf-class="page-item {{ store.searchPage === 1 ? 'disabled' : '' }}">
          <a class="page-link"
             t-on-click="() => this.updateCurrentPage('previous')">Previous</a>
        </li>

          <!--Not showing all pages, overflow of pages displayed as an elipse-->
          <t t-foreach="store.visiblePages" t-as="page" t-key="page_index">
            <t t-if="page === '...'">
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            </t>

            <t t-else="">
                <li t-attf-class="page-item {{ store.searchPage === page ? 'active' : '' }}">
                    <a class="page-link"
                       href="#"
                       t-on-click="(ev) => this.onPageNumberClick(page, ev)">
                        <t t-esc="page"/>
                    </a>
                </li>
            </t>
          </t>

        <!-- 'Next' page Button-->
        <li t-attf-class="page-item {{ store.searchPage === store.numberOfPages ? 'disabled' : '' }}">
          <a class="page-link"
             t-on-click="() => this.updateCurrentPage('next')">Next</a>
        </li>
      </ul>
    </nav>
  `;

    static components = {};
    store = useState(store);

    setup() {
        this.orm = useService("orm");
        this.state = useState({pageName: "SnapShotList"});
    }

    onPageNumberClick(page, ev) {
        if (ev) {
            ev.preventDefault();
        }
        this.updateCurrentPage(page);
    }

    updateCurrentPage(pageNumber) {
        const cur = this.store.searchPage;
        let next;
        if (pageNumber === "previous") {
            next = Math.max(1, cur - 1);
        } else if (pageNumber === "next") {
            next = Math.min(this.store.numberOfPages, cur + 1);
        } else {
            next = pageNumber;
        }
        if (next === cur) {
            return;
        }
        this.store.searchPage = next;
        this.store.executeSearch(this);
    }
}
