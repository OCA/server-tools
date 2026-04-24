/** @odoo-module **/
import { Component, useState, onWillStart, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { createSnapshotInstance } from "./dashboard_helpers";

export class CreateSnapShot extends Component {
    static template = xml`
        <!--You have to include the stylesheet below for the icons, if you don't you will be forced to paste the svg-->
        <script src="https://kit.fontawesome.com/2263bf088c.js" crossorigin="anonymous" />

        <header>
          <div class="row">
            <div class="col">
              <button class="btn btn-outline-warning me-2 create-back-to-snapshots"
                      t-on-click="() => this.backToSnapshots()">
                <i class="fa-regular fa-circle-left" style="margin-right: 6px" />Back to Snapshots
              </button>
            </div>
          </div>
        </header>

        <!--Start of the body of the form-->
        <body class="create-snapshot-form-body">
          <!--Added overflow-auto to form, all data doesn't fit into the form so we must be able to scroll-->
          <div class="create-snapshot-form overflow-auto">
              <div class="card">
                  <div class="card-body">
                    <!--Domain Selector switch-->
                    <div class="mb-3">
                      <div class="dropdown">
                        <button class="btn btn-secondary dropdown-toggle"
                                type="button"
                                data-bs-toggle="dropdown"
                                aria-expanded="false">
                          Select Domain
                        </button>

                        <ul class="dropdown-menu dropdown-menu-dark">
                          <t t-foreach="state.existingDomainNames"
                             t-as="domainName"
                             t-key="domainName">
                             <li t-on-click="() => this.assignStateVariables('domain', domainName)">
                               <a class="dropdown-item" href="#"><t t-esc="domainName"/></a>
                             </li>
                          </t>
                        </ul>
                      </div>
                    </div>

                    <!--The Domain selected will display on the card below-->
                    <t t-if="state.domainName">
                        <div class="mb-3">
                            <div class="card">
                              <div class="card-body">
                                  <span class="badge rounded-pill text-bg-primary"
                                        style="margin-right: 2px"><t t-esc="state.domainName"/>
                                  </span>
                              </div>
                            </div>
                        </div>
                    </t>
                  </div>
              </div>

              <!--Target Selector switch or Create a new Target-->
              <div class="card">
                  <div class="card-body">
                    <div class="mb-3">
                      <div class="dropdown">
                        <button t-attf-class="btn btn-secondary dropdown-toggle {{ state.domainName ? '' : 'disabled' }}"
                                type="button"
                                data-bs-toggle="dropdown"
                                aria-expanded="false">
                          Select Target
                        </button>

                        <ul class="dropdown-menu dropdown-menu-dark">
                          <t t-foreach="state.domainTargetNames"
                             t-as="targetName"
                             t-key="targetName">
                             <li t-on-click="() => this.assignStateVariables('target', targetName)">
                               <a class="dropdown-item" href="#"><t t-esc="targetName"/></a>
                             </li>
                          </t>
                        </ul>
                      </div>
                    </div>

                    <!--The existing target selected will display in the card below-->
                    <t t-if="state.targetName">
                        <div class="mb-3">
                            <div class="card">
                              <div class="card-body">
                                  <span class="badge rounded-pill text-bg-primary"
                                        style="margin-right: 2px"><t t-esc="state.targetName"/>
                                  </span>
                              </div>
                            </div>
                        </div>
                    </t>
                  </div>
              </div>

              <!--Inspector Details-->
              <div class="card">
                  <div class="card-body">
                    <div class="mb-3">
                      <div class="dropdown">
                        <button t-attf-class="btn btn-secondary dropdown-toggle {{ state.targetName ? '' : 'disabled' }}"
                                type="button"
                                data-bs-toggle="dropdown"
                                aria-expanded="false">
                          Select Inspector
                        </button>
                        <ul class="dropdown-menu dropdown-menu-dark">
                          <t t-foreach="state.existingInspectorNames"
                             t-as="inspector"
                             t-key="inspector.id">
                             <li t-on-click="() => this.assignStateVariables('inspector', inspector.inspectorName)">
                               <a class="dropdown-item" href="#"><t t-esc="inspector.inspectorName"/></a>
                             </li>
                          </t>
                        </ul>
                      </div>
                    </div>

                    <!-- If an existing inspector was selected it will show on the below card-->
                    <t t-if="state.firstName">
                        <div class="mb-3">
                            <div class="card">
                              <div class="card-body">
                                  <span class="badge rounded-pill text-bg-primary"
                                        style="margin-right: 2px"><t t-esc="state.firstName + ' ' + state.lastName"/>
                                  </span>
                              </div>
                            </div>
                        </div>
                    </t>
                  </div>
              </div>

              <!-- Section Selector switch-->
              <t t-if="state.domainName and state.targetName">
                  <div class="card-footer text-body-secondary submit-and-create-btn">
                      <t t-if="state.domainName and
                                state.targetName and
                                state.firstName and
                                state.lastName">
                        <!-- Disable button after 1st click to prevent multiple submissions-->
                        <button t-attf-class="btn btn-outline-danger answer-questions-btn {{ state.submitClicked === true ? 'disabled' : '' }}"
                          t-on-click="() => this.createNewSnapShot()">
                          <i class="fa-solid fa-circle-play answer-questions-icon" />Answer Questions

                          <!-- Adding a spinner/loader while the Snapshot is being created and the user redirected to the questions-->
                          <t t-if="state.submitClicked">
                            <div class="d-flex align-items-center text-danger answer-questions-spinner">
                                <div class="spinner-border ms-auto" aria-hidden="true" role="status" />
                            </div>
                          </t>
                        </button>
                    </t>
                  </div>
              </t>
          </div>
        </body>
    `;

    // Javascript of the component
    static props = {
        data: {},
        parentState: "",
    };

    setup() {
        this.state = useState({
            pageName: "createSnapshotHomePage",
            pageData: {},
            allDomainInstances: {},
            allTargetInstances: {},
            allInspectorInstances: {},
            existingDomainNames: [],
            domainTargetNames: [],
            domainSectionNames: [],
            existingInspectorNames: [],
            domainSectionQuestions: [],
            domainName: "",
            targetName: "",
            firstName: "",
            lastName: "",
            sectionName: "",
            submitClicked: false,
            newSnapShotData: {},
        });

        // Need this service to retrieve db records
        this.orm = useService("orm");

        // Get all the snapshot instances just before the page renders.
        onWillStart(async () => {
            // Getting all the current domain instances in the DB.
            await this.getAllDomainInstances().then((result) => {
                this.state.allDomainInstances = result;
                for (const domain of this.state.allDomainInstances) {
                    this.state.existingDomainNames.push(domain.name);
                }
            });

            // Getting all the current target instances in the DB.
            await this.getAllTargetInstances().then((result) => {
                this.state.allTargetInstances = result;
            });

            // Get all existing inspectors
            await this.getActiveInspectors().then((result) => {
                this.state.allInspectorInstances = result;
                for (const inspector of this.state.allInspectorInstances) {
                    this.state.existingInspectorNames.push({
                        inspectorName: `${inspector.forename} ${inspector.surname}`,
                        id: inspector.id,
                    });
                }
            });
        });
    }

    getAllDomainInstances() {
        //return this.orm.searchRead('audit.domain', [], [])
        return this.orm.searchRead("audit.domain", [], []).then((result) => {
            return result.map((domain) => {
                // Ensure target_ids is populated
                if (!domain.target_ids.length && domain.target_rel_ids.length) {
                    domain.target_ids = domain.target_rel_ids;
                }
                return domain;
            });
        });
    }

    getActiveInspectors() {
        return this.orm.searchRead("audit.inspector", [["active", "=", true]], []);
    }

    getAllTargetInstances() {
        return this.orm.searchRead("audit.target", [], []);
    }

    async getTargetIDInstances(targetIDS) {
        this.state.domainTargetNames = [];
        const targetInstances = await this.orm.read("audit.target", targetIDS, ["name", "domain_id", "snapshot_ids"]);
        targetInstances.forEach((entry) => {
            this.state.domainTargetNames.push(entry.name);
        });
    }

    async getSectionIDInstances(domainID) {
        let number = 0;
        this.state.domainSectionNames = [];
        this.state.domainSectionQuestions = [];

        // First, get (search) the snapshot_section ids we are interested in
        const sectionIDs = await this.orm.search("audit.snapshot_section", [["domain_id", "=", domainID]]);

        // Secondly, see (read) only the attribute values we need for each snapshot_section we are interested in
        const snapshot_sections = await this.orm.read("audit.snapshot_section", sectionIDs, [
            "display_name",
            "snapshot_question_ids",
        ]);

        for (const snapshot_section of snapshot_sections) {
            if (
                !this.state.domainSectionNames.some((section) => section.sectionName === snapshot_section.display_name)
            ) {
                this.state.domainSectionNames.push({
                    sectionName: snapshot_section.display_name,
                    id: snapshot_section.id,
                });

                const questionIDs = snapshot_section.snapshot_question_ids;
                if (questionIDs.length > 0) {
                    const questions = await this.orm.read("audit.snapshot_question", questionIDs, [
                        "prompt",
                        "snapshot_section_id",
                    ]);

                    questions.forEach((question) => {
                        const question_data = {
                            id: number++,
                            sectionName: question.snapshot_section_id[1],
                            prompt: question.prompt,
                        };
                        this.state.domainSectionQuestions.push(question_data);
                    });
                }
            }
        }
    }

    resetStateVariables() {
        this.state.targetName = "";
        this.state.sectionName = "";
    }

    assignStateVariables(option, value) {
        // Logic for when a domain is selected
        if (option === "domain") {
            // First clean out existing data
            this.state.targetName = "";
            this.state.sectionName = "";
            // Now start adding new data
            this.state.domainName = value;
            const domainInstance = this.state.allDomainInstances.find((element) => element.name === value);
            const combinedTargetIDs = [...new Set([...domainInstance.target_ids, ...domainInstance.target_rel_ids])];
            // Call the relevant function to retrieve the Target instances if there were any target id's for this domain
            this.getTargetIDInstances(combinedTargetIDs);
            // Call the relevant function to retrieve the Snapshot section instances for the selected Domain
            this.getSectionIDInstances(domainInstance.id);
        }

        // Logic for when a target is selected
        if (option === "target") {
            this.state.targetName = value;
        }

        // Logic for when an inspector is selected or a new one is created
        if (option === "inspector") {
            this.state.firstName = value.split(" ")[0];
            this.state.lastName = value.split(" ")[1];
        }

        if (option === "section") {
            this.state.sectionName = value;
        }
    }

    async createNewSnapShot() {
        this.state.submitClicked = true;

        // Find domain object
        const domainObject = this.state.allDomainInstances.find(
            (domain) => domain.display_name === this.state.domainName,
        );

        // Find target object, if not found then new target to be created
        const targetObject = this.state.allTargetInstances.find((target) => target.name === this.state.targetName);

        // Find inspector object, if none, a new inspector is to be created
        const inspectorObject = this.state.allInspectorInstances.find(
            (inspector) => inspector.forename === this.state.firstName && inspector.surname === this.state.lastName,
        );

        // Setting state data object which will be sent to the controller to create the new Snapshot Instance
        this.state.newSnapShotData = {
            domain_id: domainObject.id,
            target_id: targetObject ? targetObject.id : null,
            new_target_name: this.state.targetName,
            inspector_id: inspectorObject ? inspectorObject.id : null,
            new_inspector_name: {
                forename: this.state.firstName,
                surname: this.state.lastName,
            },
        };

        // Call createSnapshotInstance from dashboard_helpers.js to take care of the snapshot creation
        const newSnapshot = await createSnapshotInstance(this.state.newSnapShotData, { orm: this.orm })

        setTimeout(() => {
                // Update the props of the `snapshot` component
                console.log("dashboard.js::createSnapshot > state.PageData props ", newSnapshot);
                this.state.pageData = newSnapshot;
                // Change page to 'SnapShotInstance' to start answering the questions
                this.state.pageName = "SnapShotInstance";
            }, 3000);
        // Set the correct page in the `dashboard.js/parent` component and also give it the new snapshot data
        this.props.parentState.pageData = newSnapshot;
        this.props.parentState.pageName = "SnapShotInstance";
    }

    backToSnapshots() {
        this.props.parentState.pageName = "auditHomePage";
        this.resetStateVariables();
    }
}
