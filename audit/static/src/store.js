/** @odoo-module **/
import {reactive} from "@odoo/owl";

const SEARCH_DEBOUNCE_MS = 200;

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
        this._lastServedSearchKey = null;
    }

    _searchRequestId = 0;
    _searchInFlight = null;
    _searchInFlightKey = null;
    _lastServedSearchKey = null;

    _searchDebounceHandle = null;
    _pendingDebouncedApi = null;
    _debouncedResultPromise = null;
    _resolveDebouncedResult = null;

    _clearSearchDebounce() {
        if (this._searchDebounceHandle) {
            clearTimeout(this._searchDebounceHandle);
            this._searchDebounceHandle = null;
        }
        this._pendingDebouncedApi = null;
        if (this._resolveDebouncedResult) {
            this._resolveDebouncedResult();
            this._resolveDebouncedResult = null;
        }
        this._debouncedResultPromise = null;
    }

    /**
     * @param {object} api
     * @param {{ immediate?: boolean }} [options] Use `immediate: true` for initial load, pagination, and
     *  navigations where the UI must not wait for debounce; leave default for the date filter to avoid
     *  a storm of duplicate RPCs (spurious `change` after re-renders, etc.).
     * Coalesces identical in-flight key; discards responses superseded by a newer request.
     */
    async executeSearch(api, {immediate = false} = {}) {
        if (immediate) {
            this._clearSearchDebounce();
            return this._doExecuteSearch(api, {fromImmediate: true});
        }
        this._pendingDebouncedApi = api;
        if (!this._debouncedResultPromise) {
            this._debouncedResultPromise = new Promise((resolve) => {
                this._resolveDebouncedResult = resolve;
            });
        }
        if (this._searchDebounceHandle) {
            clearTimeout(this._searchDebounceHandle);
        }
        this._searchDebounceHandle = setTimeout(() => {
            this._searchDebounceHandle = null;
            const api0 = this._pendingDebouncedApi;
            this._pendingDebouncedApi = null;
            const resolve0 = this._resolveDebouncedResult;
            this._resolveDebouncedResult = null;
            this._debouncedResultPromise = null;
            (async () => {
                try {
                    await this._doExecuteSearch(api0, {fromImmediate: false});
                } finally {
                    if (resolve0) {
                        resolve0();
                    }
                }
            })();
        }, SEARCH_DEBOUNCE_MS);
        return this._debouncedResultPromise;
    }

    async _doExecuteSearch(api, {fromImmediate}) {
        const key = this.searchString;
        if (this._searchInFlight && this._searchInFlightKey === key) {
            return this._searchInFlight;
        }
        if (!fromImmediate && key === this._lastServedSearchKey) {
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
            this.searchPage = results.newPageNumber;
            this.searchedSnapshots = results.snapshots;
            this._lastServedSearchKey = key;
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
