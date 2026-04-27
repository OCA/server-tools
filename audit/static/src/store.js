/** @odoo-module **/
import { reactive } from "@odoo/owl";

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
     * Page numbers (and "..." entries) for pagination, derived from numberOfPages and searchPage.
     */
    get visiblePages() {
        const total = this.numberOfPages;
        const current = this.searchPage;
        if (total < 1) {
            return [];
        }
        if (total === 1) {
            return [1];
        }
        if (total <= 7) {
            return Array.from({length: total}, (_, i) => i + 1);
        }
        if (current <= 4) {
            return [1, 2, 3, 4, 5, "...", total];
        }
        if (current >= total - 3) {
            return [
                1,
                "...",
                total - 4,
                total - 3,
                total - 2,
                total - 1,
                total,
            ];
        }
        return [1, "...", current - 1, current, current + 1, "...", total];
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
    /**
     * This will submit the search to the backend, and update the relevant data
     */
    async executeSearch(api) {
        const results = await api.orm.call("audit.snapshot", "custom_search", [this.searchString]);
        this.numberOfPages = results.numberOfPages;
        const returnedPage = results.newPageNumber;
        this.searchPage =
            returnedPage != null && returnedPage > 0 ? returnedPage : 1;
        this.searchedSnapshots = results.snapshots;
    }
}

// Make this available to all components and reactive
export const store = reactive(new Store());
