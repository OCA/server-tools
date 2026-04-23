/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps, xml } from "@odoo/owl";
//In order to get data from our database we need a service, hence the import of useService below
import { useService } from "@web/core/utils/hooks";
import {orderCurrentSnapshotInstanceData, PageComponent, prepareAllSnapshotQuestions} from "./dashboard_helpers";
import { store } from "../../store";

export class SnapshotList extends Component {
    static template = xml`
        <!-- A table to display all Audit Snapshot records and their relevant information -->
        <div class="snapshot-list-table">
            <body class="snapshot-list-table-body">
              <div class="row m-2">
                  <div class="col">
                      <table class="table table-striped table-hover">
                        <thead>
                            <!-- This first row is for all the column headers of the table-->
                            <tr>
                              <th scope="col">Display Name</th>
                              <th scope="col">Target</th>
                              <th scope="col">Domain</th>
                              <th scope="col">Inspector</th>
                              <th scope="col">Status</th>
                              <th scope="col">Percentage Score</th>
                              <th scope="col">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                          <tr
                              t-foreach="store.searchedSnapshots"
                              t-as="snapshotInstance"
                              t-key="snapshotInstance.id">
                              <td data-cell="name" t-esc="snapshotInstance.display_name.substring(0, snapshotInstance.display_name.indexOf(' ')) + ' ' + snapshotInstance.date_conducted.substring(8, 10) + snapshotInstance.date_conducted.substring(4, 7) + '-' + snapshotInstance.date_conducted.substring(0, 4)" />
                              <td data-cell="target" t-esc="snapshotInstance.target_id[1]" />
                              <td data-cell="domain" t-esc="snapshotInstance.domain_id[1]" />
                              <td data-cell="inspector" t-esc="snapshotInstance.inspector_id[1]" />
                              <td data-cell="status">
                                  <span class="locks-in-span">
                                      <i t-attf-class="{{ snapshotInstance.locked ? 'fa-solid fa-lock' : 'fa-solid fa-lock-open' }}"
                                         t-attf-style="{{ snapshotInstance.locked ? 'color: #FE0000' : 'color: #6ECCAF' }}" />
                                  </span>
                              </td>
                              <td data-cell="score">
                                <span class="snapshot-list-percentage-display"
                                      t-attf-style="{{ ((snapshotInstance.percentage_score * 100) >= 85 and snapshotInstance.locked) ? 'color: #6ECCAF' : 'color: #FE0000' }}"
                                      t-esc="this.showPassOrFail(snapshotInstance)" />
                                <span class="snapshot-list-percentage-display"
                                      t-esc="(snapshotInstance.percentage_score * 100).toFixed(0) + '%'" />
                              </td>
                              <td data-cell="actions" class="snapshot-list-buttons">
                                  <!-- If you don't call the function below like it is done below, then the function call acts like a computed property in Vue-->
                                  <!-- in that it gets called straight away and multiple times.  Notice also then when we call the function we use "this" otherwise-->
                                  <!-- owl thinks we are re-declaring a function and does very weird things-->
                                  <button class="btn btn-outline-info me-2 view-questions view-questions-button"
                                          t-on-click="() => this.viewSnapShotQuestions(snapshotInstance)">
                                      <i class="fa-solid fa-glasses" style="margin-right: 6px" />View Questions
                                  </button>
    <!--                          Only show this button if an audit instance is locked, ergo, it has been submitted-->
                                  <t t-if="snapshotInstance.locked">
                                      <button class="btn btn-outline-secondary view-questions summary-button"
                                              t-on-click="() => this.viewSnapshotSummary(snapshotInstance)">
                                          <i class="fa-solid fa-book" style="margin-right: 4px"/>Summary
                                          <!-- Only display this badge if the snapshot has questions with comments filled in-->
                                          <t t-if="snapshotInstance.questions_with_comments > 0">
                                              <span class="badge question-count-badge rounded-pill">
                                                <div class="question-count-badge-value" t-esc="snapshotInstance.questions_with_comments" />
                                              </span>
                                          </t>
                                      </button>
                                  </t>
                              </td>
                          </tr>
                        </tbody>
                      </table>
                  </div>
              </div>
            </body>
            <!--Calling the PageComponent to take care of pagination-->
            <PageComponent pages="state.pages" currentPage="state.currentPage" />
        </div>
    `;
    static components = { PageComponent };

    store = useState(store);

    setup() {
        this.state = useState({
            allSnapShotInstances: {},
            pageName: "SnapShotList",
            pageData: [],
            pages: null,
            currentPage: 1,
        });
        this.orm = useService("orm");

        // Fetch all snapshot instances before the page renders.
        onWillStart(async () => {
            // Setting `allSnapShotInstances` of this component to the data passed in from `Dashboard` via props
            this.state.allSnapShotInstances = store.searchedSnapshots;
            this.state.pages = store.numberOfPages;
        });

        onWillUpdateProps((nextProps) => {
            this.state.allSnapShotInstances = nextProps.data;
            this.state.pages = nextProps.pages;
        });
    }

    async viewSnapShotQuestions(snapshot) {
        // Emit event, Dashboard will pick up and handle it
        const orderedData = await orderCurrentSnapshotInstanceData(snapshot, {orm: this.orm});
        setTimeout(() => {
            this.props.parentState.pageData = orderedData
            this.props.parentState.pageName = "SnapShotInstance";
        }, 800);
    }

    async viewSnapshotSummary(snapshotInstance) {
        // Prepare the data the parent component (dashboard.js) is going to need
        this.props.parentState.pageData = await prepareAllSnapshotQuestions([snapshotInstance], {orm: this.orm})
        // Change page to 'SnapshotSummary'
        this.props.parentState.pageName = "SnapshotSummary"
    }

    showPassOrFail(snapshot) {
        if (snapshot.percentage_score * 100 >= 85 && snapshot.locked) {
            return "PASS - ";
        } else if (snapshot.percentage_score * 100 < 85 && snapshot.locked) {
            return "FAIL - ";
        } else {
            return "";
        }
    }
}
