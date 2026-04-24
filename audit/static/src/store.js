/** @odoo-module **/
import {reactive} from "@odoo/owl";

/**
 * This allows central storage of state
 */
class Store {
    // These fields are for the search capability
    searchText = null;
    searchDate = null;
    searchStatus = null;
    searchPage = 1;

    // This will get returned always by the search query
    numberOfPages = 1;
    searchedSnapshots = [];

    /**
     * A helper function to determine which pages to display by the pagination component
     */
    get visiblePages() {
        const total = this.numberOfPages;
        const current = this.searchPage;

        if (!total || total < 1) {
            return [];
        }
        const pages = [];
        // Always show first page
        pages.push(1);

        // Near the start
        if (current <= 3) {
            for (let i = 2; i <= Math.min(3, total - 1); i++) {
                pages.push(i);
            }
            if (total > 4) {
                pages.push("...");
            }
        }
        // Near the end
        else if (current >= total - 2) {
            if (total > 4) {
                pages.push("...");
            }
            for (let i = Math.max(2, total - 2); i < total; i++) {
                pages.push(i);
            }
        }
        // Middle
        else {
            pages.push("...");
            pages.push(current - 1);
            pages.push(current);
            pages.push(current + 1);
            pages.push("...");
        }

        // Always show the last page if more than 1 page
        if (total > 1) {
            pages.push(total);
        }

        return pages;
    }

    /**
     * This will return the string that we send to the search endpoint
     */
    get searchString() {
        return JSON.stringify({
            searchText: this.searchText,
            searchDate: this.searchDate,
            searchStatus: this.searchStatus,
            searchPage: this.searchPage,
        });
    }

    /**
     * Revert back to defaults
     */
    resetSearchFields() {
        this.searchText = null;
        this.searchDate = null;
        this.searchStatus = null;
        this.searchPage = 1;
    }

    _searchRequestId = 0;
    _searchInFlight = null;
    _searchInFlightKey = null;

    /**
     * Submit the search to the backend and update list state. Coalesces identical
     * concurrent calls; discards responses superseded by a newer request.
     */
    async executeSearch(api) {
        const key = this.searchString;
        if (this._searchInFlight && this._searchInFlightKey === key) {
            return this._searchInFlight;
        }
        this._searchInFlightKey = key;
        const orm = api?.orm;
        if (!orm?.call) {
            this._searchInFlightKey = null;
            return;
        }
        const run = (async () => {
            const reqId = ++this._searchRequestId;
            const results = await orm.call("audit.snapshot", "custom_search", [key]);
            if (reqId !== this._searchRequestId) {
                return;
            }
            this.numberOfPages = results.numberOfPages;
            this.searchPage = results.newPageNumber;
            this.searchedSnapshots = results.snapshots;
        })();
        this._searchInFlight = run;
        try {
            await run;
        } finally {
            if (this._searchInFlight === run) {
                this._searchInFlight = null;
                this._searchInFlightKey = null;
            }
        }
    }
}

// Make this available to all components and reactive
export const store = reactive(new Store());
