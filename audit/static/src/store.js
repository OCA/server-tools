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

    _cacheVisibleKey = null;
    _cacheVisible = null;

    _normEmpty(value) {
        if (value === "" || value === undefined) {
            return null;
        }
        return value;
    }

    _normPage(value) {
        const p = Number(value);
        if (Number.isFinite(p) && p >= 1) {
            return p;
        }
        return 1;
    }

    /**
     * A helper function to determine which pages to display by the pagination component
     */
    get visiblePages() {
        const total = this.numberOfPages;
        const current = this.searchPage;
        const k = `${total}|${current}`;
        if (this._cacheVisibleKey === k && this._cacheVisible) {
            return this._cacheVisible;
        }

        if (!total || total < 1) {
            this._cacheVisibleKey = k;
            this._cacheVisible = [];
            return this._cacheVisible;
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

        this._cacheVisibleKey = k;
        this._cacheVisible = pages;
        return pages;
    }

    /**
     * Stable JSON for the search RPC. Normalizes null/"" so t-model and the server
     * do not produce a different string on every render (which caused RPC storms).
     */
    get searchString() {
        return JSON.stringify({
            searchText: this._normEmpty(this.searchText),
            searchDate: this._normEmpty(this.searchDate),
            searchStatus: this._normEmpty(this.searchStatus),
            searchPage: this._normPage(this.searchPage),
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
        this._lastServedSearchKey = null;
    }

    _searchRequestId = 0;
    _searchInFlight = null;
    _searchInFlightKey = null;
    _lastServedSearchKey = null;

    /**
     * @param {object} api
     * @param {{ force?: boolean }} [options] Pass `force: true` when the same filter key must be
     *  refetched (e.g. returning to the dashboard after editing a snapshot).
     * Coalesces identical in-flight key; discards responses superseded by a newer request.
     */
    async executeSearch(api, {force = false} = {}) {
        return this._doExecuteSearch(api, {force});
    }

    async _doExecuteSearch(api, {force}) {
        const key = this.searchString;
        if (this._searchInFlight && this._searchInFlightKey === key) {
            return this._searchInFlight;
        }
        if (!force && key === this._lastServedSearchKey) {
            return;
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
            this.searchPage = this._normPage(results.newPageNumber);
            this.searchedSnapshots = results.snapshots;
            this._lastServedSearchKey = this.searchString;
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
