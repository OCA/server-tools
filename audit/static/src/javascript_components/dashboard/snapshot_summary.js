/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { store } from "../../store";

export class SnapshotSummary extends Component {
    static template = xml`
        <div class="snapshot-header-footer">
            <button class="btn btn-outline-warning back-to-snapshots" 
                    t-on-click="() => this.backToAuditDashboard()">
                <i class="fa-regular fa-circle-left" style="margin-right: 6px" />Back To Snapshots
            </button>
        </div>
        
        <!-- A table to display details regarding each question in the snapshot -->
        <div class="summary-page">
            <t t-foreach="state.questionsWithComments"
               t-as="entry"
               t-key="entry.sectionName">
                <div class="card snapshot-summary-card">
                  <div class="card-body" style="background-color: #C7C8CC !important; border-radius: 5px !important">
                    <h5 class="card-title summary-card-title"
                        style="color: lightslategrey; font-weight: 700; max-width: 295px">
                        <div t-esc="entry.sectionName" />
                        <span class="badge section-score">
                            Score: <t t-esc="this.calculateSectionScore(entry) + '%'" />
                        </span>
                    </h5>
                    
                    <!-- Card body and text contains details for each question in the snapshot-->
                    <div class="card-text">
                        <body class="questions-form-body summary-question-body">
                            <table class="table table-striped table-hover table-responsive summary-table">
                                <!--If a section has no commented questions then we don't want to display the column headers-->
                                <t t-if="this.commentedQuestionsOnly(entry)">
                                    <thead>
                                        <tr>
                                          <th scope="col">Question</th>
                                          <th scope="col">Score</th>
                                          <th scope="col">Comments</th>
                                          <th scope="col">Image</th>
                                        </tr>
                                    </thead>
                                </t>
                                
                                <tbody>
                                    <tr
                                      t-foreach="entry.questions"
                                      t-as="question"
                                      t-key="question.id">
                                      <!--Only show questions that have comments-->
                                      <t t-if="question.comment">
                                          <td>
                                          <div class="card-title summary-question"
                                               data-bs-toggle="tooltip"
                                               data-bs-placement="bottom"
                                               data-bs-custom-class="tooltip-primary"
                                               t-attf-title="{{ question.questionPrompt }}">
                                               <t class="summary-question" t-esc="question.questionPrompt" />
                                          </div>
                                          </td>
                                          <td style="text-align: center"><span class="question-score" t-esc="this.displayQuestionScore(question)" /></td>
                                          <td>
                                               <div class="summary-question" t-esc="question.comment" />
                                          </td>
                                          <td style="text-align: left">
                                              <!--If there is an image display a thumbnail of it, else display a default icon-->
                                              <t t-if="question.image">
                                                  <img t-attf-id="{{ question.id }}"
                                                       class="summary-image-thumbnail"
                                                       t-on-click="() => this.resizeImage(question.id)"
                                                       src="" />
                                              </t>
                                              <t t-else="">
                                                  <i class="fa-regular fa-image" />
                                              </t>
                                          </td>
                                      </t>
                                    </tr>
                                </tbody>
                                
                            </table>
                        </body>
                    </div>
                  </div>
                </div>
            </t>
            
            <!--Finally display the snapshot score-->
            <div class="card snapshot-final-score-footer">
              <div class="card-body" style="max-height: 45px; background-color: #0C2D57 !important; border-radius: 5px !important;">
                <h5 class="card-title summary-card-title" style="color: lightslategrey; font-weight: 500">
                    Snapshot Score
                    <span class="badge final-snapshot-score">
                        <t t-esc="state.snapshotScore.toFixed(2) + '%'" />
                    </span>
                </h5>
              </div>
            </div>
        </div>
    `;

    static props = {
        data: {},
        parentState: "",  // parentState is the parents (dashboard.js) state, received here by the child component
    };

    setup() {
        this.store = useState(store)
        this.orm = useService("orm")

        this.state = useState({
            pageName: "SnapshotSummary",
            pageData: [],
            questionsWithComments: [],
            snapshotScore: 0,
        });

        onWillStart(() => {
            this.state.snapshotScore = this.props.data[0].percentage_score * 100;
            this.state.pageData = this.props.data;
            // Extract only what is needed
            this.getQuestions(this.state.pageData);
        });

        // Find html elements that should have images, convert those images and then display them
        onMounted(() => {
            this.state.questionsWithComments.forEach((entry) => {
                if (entry.questions) {
                    entry.questions.forEach((question) => {
                        this.convertBase64ToFile(question);
                    });
                }
            });
        });
    }

    getQuestions(data) {
        let id = 0;
        for (const [, value] of Object.entries(data[0].questions)) {
            const questions = [];
            const sectionQuestions = value;
            // Skip sections with no questions (handles empty arrays on subsequent calls)
            if (!sectionQuestions || sectionQuestions.length === 0) {
                continue;
            }

            // A set of `sectionQuestions` will obviously all have the same section, get the section Name from the first entry
            const sectionName = sectionQuestions[0].snapshot_section_id[1];
            sectionQuestions.forEach((question) => {
                questions.push({
                    id: id++,
                    sectionName: question.snapshot_section_id[1],
                    questionPrompt: question.prompt,
                    value: question.value,
                    comment: question.comment,
                    image: question.image ? question.image : null,
                });
            });
            this.state.questionsWithComments.push({
                sectionName: sectionName,
                questions: questions,
            });
        }
    }

    convertBase64ToFile(question) {
        // Find the right question
        let questionElement = {};
        for (const entry of this.state.questionsWithComments) {
            if (entry.questions) {
                for (const value of entry.questions) {
                    if (value.id === question.id) {
                        questionElement = value;
                    }
                }
            }
        }
        const uploadedImage = document.getElementById(questionElement.id);
        if (uploadedImage) {
            uploadedImage.src = `data:image/png;base64, ${question.image}`;
        }
    }

    calculateSectionScore(entry) {
        let totalWeight = 0;
        let totalValue = 0;
        entry.questions.forEach((question) => {
            totalWeight += 1
            totalValue += question.value;
        });
        return ((totalValue / totalWeight) * 100).toFixed(2);
    }

    commentedQuestionsOnly(entry) {
        let result = 0;
        entry.questions.forEach((question) => {
            if (question.comment) {
                result++;
            }
        });
        // `True` will be returned if result > 0
        return result > 0;
    }

    async backToAuditDashboard() {
        await this.store.executeSearch(this);
        this.props.parentState.pageName = "auditHomePage";
    }

    displayQuestionScore(question) {
        return `${question.value * 100}%`
    }

    resizeImage(questionID) {
        const image = document.getElementById(questionID);
        if (image.style.width === "200px" && image.style.height === "200px") {
            image.style = "width: 50px; height: 50px";
        } else {
            image.style = "width: 200px; height: 200px";
        }
    }
}
