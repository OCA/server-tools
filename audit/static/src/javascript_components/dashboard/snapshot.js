/** @odoo-module **/
import {Component, onWillStart, onWillUpdateProps, useState, xml} from "@odoo/owl";
// In order to get data from our database we need a service, hence the import of useService below
import {useService} from "@web/core/utils/hooks";
import {store} from "../../store";
import {autoSaveQuestionChanges, questionApplicable, submit} from "./dashboard_helpers";

export class Snapshot extends Component {
    static template = xml`
        <script src="https://kit.fontawesome.com/2263bf088c.js" crossorigin="anonymous" />

        <!-- A bunch of cards, each displays a single question -->
        <div class="snapshot-header-footer">
            <button class="btn btn-outline-warning back-to-snapshots"
                    t-on-click="() => this.backToAuditDashboard()">
                <i class="fa-regular fa-circle-left" style="margin-right: 6px" />Back To Snapshots
            </button>
        </div>

        <div class="questions-form-body">
            <div class="questions-form">
              <div class="row m-2">
                  <div class="col">

                      <t t-foreach="this.state.questions"
                         t-as="section"
                         t-key="section.snapshot_section_name">
                          <div class="row questions-container">
                              <div class="col-sm-6 mb-3 mb-sm-0">

                                <t t-if="(typeof section.snapshot_section_name === 'string')">
                                    <div class="alert alert-primary section-header"
                                         role="alert"
                                         style="font-size: large">
                                      <t t-esc="section.snapshot_section_name" />
                                    </div>
                                </t>
                              </div>
                          </div>

                          <!--For each section, display its questions separately-->
                          <t t-foreach="section.questions"
                             t-as="question"
                             t-key="question.number">
                              <div class="row questions-container">
                                  <div class="col-sm-6 mb-3 mb-sm-0 question-container-card">
                                    <!--For each question a card is made, the card contains all the info for the question-->
                                    <div class="card individual-question-card">
                                      <!--Making the card body of a question ghostwhite if the question is no longer applicable-->
                                      <div class="card-body"
                                           t-attf-style="{{ question.applicable ? '' : 'background: ghostwhite !important' }}; border-style: solid; border-color: #89c4ff; border-radius: 5px;">
                                          <div class="question-and-icon">
                                            <!--Logic on icon will display a locked or an unlocked padlock depending on if the snapshot has been submitted-->
                                            <span class="locks-in-span">
                                                <i t-attf-class="{{ state.allQuestionsLocked ? 'locked-icon fa-solid fa-lock' : 'unlocked-icon fa-solid fa-lock-open' }}" />
                                            </span>
                                            <!--Making the question prompt also ghostwhite if the question is no longer applicable-->
                                            <div class="badge text-wrap question-prompt"
                                                 t-attf-style="{{ question.applicable ? '' : 'background: ghostwhite !important' }}">
                                                <h4 class="card-text"><t t-esc="question.prompt" /></h4>
                                            </div>
                                          </div>

                                        <div class="card-text">
                                            <p>
                                                <t t-if="question.answer_type === 'boolean'">
                                                  <select class="form-select from-control question-answers-select needs-validation"
                                                          id="answerTypeControlCheck"
                                                          aria-label="Yes/No questions"
                                                          t-on-change="() => this.autoSaveQuestion(question)"
                                                          t-model="question.answer_yn">
                                                      <option value="" />
                                                      <option value="0">No</option>
                                                      <option value="1">Yes</option>
                                                  </select>
                                                </t>

                                                <t t-elif="question.answer_type === 'integer'">
                                                  <select class="form-select question-answers-select needs-validation"
                                                          aria-label="Star rated questions"
                                                          t-on-change="() => this.autoSaveQuestion(question)"
                                                          t-model="question.answer_star">
                                                      <option value=""/>
                                                      <option value="1">★</option>
                                                      <option value="2">★★</option>
                                                      <option value="3">★★★</option>
                                                      <option value="4">★★★★</option>
                                                  </select>
                                                </t>

                                                <t t-elif="question.answer_type === 'float'">
                                                    <div class="slider">
                                                        <input id="percentageSlider"
                                                               type="range"
                                                               style="max-width: fit-content; background: border-box"
                                                               min="0"
                                                               max="100"
                                                               step="1"
                                                               value="0"
                                                               t-on-change="() => this.autoSaveQuestion(question)"
                                                               t-model="question.answer_perc" />
                                                        <p class="slider-value"><t t-esc="question.answer_perc + '%'" /></p>
                                                    </div>
                                                </t>
                                            </p>
                                        </div>

                                        <p class="card-text questions-font">Comments:
                                            <t t-if="question.comment.length >= 1">
                                                <p t-on-click="() => { question.comment = '', this.autoSaveQuestion(question) }">
                                                    <t t-esc="question.comment ? question.comment.slice(0, 30) + '...' : ''" />
                                                </p>
                                            </t>

                                            <t t-else="''">
                                              <div>
                                                  <input placeholder="Type comments here..."
                                                         class="comment-text-box"
                                                         type="text"
                                                         t-on-change="() => this.autoSaveQuestion(question)"
                                                         t-model.lazy="question.comment"/>
                                              </div>
                                            </t>
                                        </p>

                                        <p class="card-text questions-font">
                                            <t t-if="question.img_src">
                                              <div class="my-2">
                                                <img style="width: 120px;" t-att-src="question.img_src" />
                                              </div>
                                              <div>Change picture</div>
                                            </t>

                                            <t t-else="">
                                              <div>Upload a picture</div>
                                            </t>

                                            <form class="upload-picture-form"
                                                  method="post"
                                                  enctype="multipart/form-data">
                                              <input
                                                  class="form-control form-control-sm file-upload-box"
                                                  type="file"
                                                  t-on-change="event => { this.onChangeAttach(event, {...question}), this.convertBase64ToFile(event, question) }"
                                                  name="image-upload"
                                                  accept="image/*"/>

                                            </form>
                                        </p>

                                        <!--"onerror" is added otherwise, if no image was chosen to be uploaded it leaves behind an ugly empty box, note the use of "this"-->
                                        <img t-attf-id="{{ question.id }}"
                                             class="image-thumbnail"
                                             src=""
                                             onerror="this.style.display='none'" />

                                        <div class="card-footer bg-light question-card-footer">
                                          <!--A switch to select a question to be applicable or not-->
                                          <div class="form-check form-switch">
                                              <div class="spinner-border text-primary"
                                                   role="status"
                                                   t-attf-style="{{ !state.questionApplicableLoader ? 'display: none' : '' }}" />

                                              <input class="form-check-input question-applicable"
                                                     t-attf-checked="{{ (!!question.applicable) }}"
                                                     type="checkbox"
                                                     role="switch"
                                                     id="flexSwitchCheckDefault"
                                                     t-on-click="() => this.questionApplicable(question)"/>

                                              <!--The label must change according to the "applicable" status of the question-->
                                              <t t-if="question.applicable">
                                                  <label class="form-check-label"
                                                         for="flexSwitchCheckDefault"
                                                         t-attf-style="{{ state.questionApplicableLoader ? 'display: none' : ''}}">Applicable
                                                  </label>
                                              </t>
                                              <t t-else="">
                                                  <label class="form-check-label"
                                                         for="flexSwitchCheckDefault"
                                                         t-attf-style="{{ state.questionApplicableLoader ? 'display: none' : ''}}">Excluded
                                                  </label>
                                              </t>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                              </div>
                          </t>
                      </t>
                  </div>
              </div>
            </div>

            <div class="snapshot-header-footer">
                <!--Button to call a save on every question on the page -->
                <button
                    t-attf-class="btn btn-outline-warning submit-snapshot-btn {{ state.allQuestionsLocked ? 'disabled' : '' }}"
                    data-bs-toggle="modal"
                    data-bs-target="#submitSnapshotModal">
                    <i class="fa-regular fa-floppy-disk" style="margin: 3px;" />Submit Snapshot
                    <t t-if="state.submitSnapshot">
                        <div class="d-flex align-items-center text-warning" style="margin-left: 8px;">
                            <div class="spinner-border ms-auto"
                                 style="font-size: medium;"
                                 aria-hidden="true"
                                 role="status" />
                        </div>
                    </t>

                </button>
                <!--The below modal will pop-up/modal if the user clicks on the above button -->
                <div class="modal fade" id="submitSnapshotModal">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header submit-snapshot-modal-header">
                        <h1 class="modal-title fs-5">Final Submission</h1>
                        <button type="button"
                                class="btn-close"
                                data-bs-dismiss="modal"
                                aria-label="Close" />
                      </div>

                      <div class="modal-body submit-snapshot-modal-body">
                        <p>The Snapshot audit will be submitted as it is, you will still be able to make changes to the questions. Do you wish to proceed?</p>
                      </div>

                      <div class="modal-footer submit-snapshot-modal-footer">
                        <!-- You have to add "data-bs-dismiss" to both "cancel" and "confirm" buttons else the model won't close -->
                        <button type="button"
                                class="btn btn-secondary cancel-button"
                                data-bs-dismiss="modal">cancel
                        </button>

                        <button
                            id="confirmBtn"
                            type="button"
                            class="btn btn-success confirm-button"
                            data-bs-dismiss="modal"
                            t-on-click="() => this.submitSnapshot()">
                            CONFIRM
                        </button>

                      </div>
                    </div>
                  </div>
                </div>
            </div>
        </div>
    `;

    // Javascript part of the component
    store = useState(store);

    static props = {
        data: {},
        parentState: "",
    };

    setup() {
        this.state = useState({
            pageName: "SnapShotInstance",
            pageData: {},
            questions: {},
            successfulEdit: false,
            allQuestionsLocked: false,
            submitSnapshot: false,
            defaultCount: 0,
            questionApplicableLoader: false,
        });

        this.orm = useService("orm");
        // You need the below action called `action` in order to view a separate action window
        this.action = useService("action");

        onWillStart(async () => {
            this.state.pageData = this.props.data;
            // Set `state.questions` else nothing will display
            this.state.questions = this.props.data;
            // Get the snapshot_id from the data, look up the snapshot and check if it is locked or not
            if (this.props.data[0].snapshot_id) {
                const snapshot = await this.orm.searchRead(
                    "audit.snapshot",
                    [["id", "=", this.props.data[0].snapshot_id]],
                    []
                );
                if (snapshot) {
                    const result = snapshot[0];
                    if (result.locked) {
                        this.state.allQuestionsLocked = true;
                    }
                }
            }
        });

        onWillUpdateProps(async (nextProps) => {
            // Get the updated pageData from the parent component via `nextProps`
            this.state.pageData = nextProps.data;
            this.state.questions = nextProps.data;
        });
    }

    async toQuestionFormView(question) {
        this.action.doAction({
            name: "Question Details",
            type: "ir.actions.act_window",
            res_model: "audit.snapshot_question",
            views: [[false, "form"]],
            target: "new",
            res_id: question.id,
        });
    }

    async backToAuditDashboard() {
        await this.store.executeSearch(this);
        this.props.parentState.pageName = "auditHomePage";
    }

    convertFileToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const fileReader = new FileReader();
            fileReader.readAsDataURL(file);

            fileReader.onload = () => {
                resolve(fileReader.result);
            };

            fileReader.onerror = (error) => {
                reject(error);
            };
        });
    };

    convertBase64ToFile(event, question) {
        const uploadedImage = document.getElementById(question.id);
        const blob = new Blob([event.target.files[0]], {type: "image/jpeg"});
        const blobURL = URL.createObjectURL(blob);
        // Have to have `.style.display = block` here and not in the css else the thumbnail won't show
        uploadedImage.style.display = "block";
        uploadedImage.src = blobURL;
    }

    // There is a t-on-change directive for the <input/> html tag which ensures that when a file is attached
    // a change event is fired, that change event is `captured` here so that we can encode the image before
    // we try and submit it to the BE.
    async onChangeAttach(event, question) {
        const pictureFile = event.target.files[0];
        const base64EncodedFile = await this.convertFileToBase64(pictureFile);
        // Save the new image to the snapshot question
        this.autoSaveQuestion(question, base64EncodedFile);
    }

    // Select between Applicable and Excluded for a particular question
    async questionApplicable(question) {
        await questionApplicable(question, {orm: this.orm});
    }

    autoSaveQuestion(question, image) {
        autoSaveQuestionChanges(question, image, {orm: this.orm});
    }

    async submitSnapshot() {
        // Before we allow a submit we must check that relevant fields have been completed
        const errors = document.querySelectorAll(".needs-validation");
        let amountOfErrors = errors.length;

        errors.forEach((error) => {
            if (error.value === "") {
                error.style =
                    "border-style: groove; border-color: red !important; border-radius: 5px !important; border-width: 3px !important";
            } else {
                error.style =
                    "border-style: groove; border-color: green !important; border-radius: 5px !important; border-width: 3px !important";
                amountOfErrors -= 1;
            }
        });

        // If all validation is good then we can submit the snapshot
        if (amountOfErrors <= 0) {
            try {
                // Set this to get the spinner turning
                this.state.submitSnapshot = true;
                // Submit the snapshot and lock it
                await submit(this.state.questions, true, {orm: this.orm});
                // Refresh the search
                this.store.resetSearchFields();
                this.store.executeSearch({orm: this.orm});
                // Set the page of the parent component (dashboard.js) to `auditHomePage`
                this.props.parentState.pageName = "auditHomePage";
            } catch (e) {
                console.log("snapshot.js::submitSnapshot::");
                throw new Error(
                    `Something went wrong while trying to submit the snapshot: , ${e}`
                );
            }
        } else {
            // eslint-disable-next-line no-alert -- simple validation message for the dashboard
            window.alert("Some of the required fields in red have not been completed!");
        }
    }
}
