- Make the jsonified_data field recomputed when:
  - any of the exported field is modified
  - the related export is changed (exported fields definition)
- This module is inspired by `connector_search_engine`
  which should be refactored on top of this.
