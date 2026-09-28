/** @odoo-module **/
import {registry} from "@web/core/registry";
import {Component, onWillStart, useState, xml} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {SnapshotList} from "./snapshot_list";
import {Snapshot} from "./snapshot";
import {CreateSnapShot} from "./create_snapshot";
import {SnapshotSummary} from "./snapshot_summary";
import {store} from "../../store";

class AuditDashboard extends Component {
    static template = xml`
        <!-- A button to create new SnapShot instances. See btn only from audit home page-->
        <t t-if="state.pageName === 'auditHomePage'">
          <div style="display: flex; max-width: 500px">
            <button
                type="button"
                class="btn btn-primary create-snapshot"
                t-on-click="() => this.selectAndCompleteAudit()">
              Select and Complete Audit
            </button>

            <div class="search-bar-text input-group search-bar">
                <!-- Custom Calendar search -->
                <div class="mx-2"><i class="fa fa-calendar" /></div>
                <input
                    type="date"
                    class="form-control"
                    t-model="store.searchDate"
                    t-on-change="() => this.store.executeSearch(this)">
                </input>
            </div>
          </div>
        </t>

        <!--Note, 'parentState' is always passed in so that child components can manipulate the -->
        <!--parent via props-->
        <t t-if="state.pageName === 'SnapShotInstance'">
          <Snapshot data="state.pageData" parentState="state"/>
        </t>

        <t t-elif="state.pageName === 'createSnapshotHomePage'">
          <CreateSnapShot data="state.pageData" parentState="state" />
        </t>

        <t t-elif="state.pageName === 'SnapshotSummary'">
          <SnapshotSummary data="state.pageData" parentState="state" />
        </t>

        <t t-elif="state.pageName !== 'createSnapshotHomePage' and
                   state.pageName !== 'SnapShotInstance' and
                   state.pageName !== 'SnapshotSummary'">

        <SnapshotList parentState="state" data="state.pageData" pages="state.pages" />
        </t>
    `;

    /** Javascript part of the component */
    static components = {
        SnapshotList,
        Snapshot,
        CreateSnapShot,
        SnapshotSummary,
    };
    store = useState(store);

    setup() {
        this.state = useState({
            pageName: "auditHomePage",
            pageData: {},
            pages: null,
            limit: 15,
            offset: 1,
            allSnapshots: {},
        });

        this.http = useService("http");
        // The orm service is necessary to call a BE function.
        this.orm = useService("orm");

        onWillStart(async () => {
            this.store.executeSearch(this);
        });
    }

    selectAndCompleteAudit() {
        this.state.pageName = "createSnapshotHomePage";
    }
}

registry.category("actions").add("audit.dashboard", AuditDashboard);
