# Input contract

This kit accepts a **local review envelope**, not a new Miilo API or SDK replacement. Supply `assessmentTime` (timezone-aware), `maxAgeSeconds` (integer 1–3600), and explicit `scope.providerIds` and `scope.workspaceIds` arrays. No wildcard or inferred workspace expansion. A work item's identity is `(providerId, id)`; matching titles and reused IDs across providers are not interchangeable.

`snapshot` is a supplied projection of the Miilo protocol 0.1 camelCase snapshot: `protocolVersion`, `snapshotId`, `observedAt`, `providers`, `workItems`. Providers need `id`, `health`, `capabilities.control`. Work items need `id`, `providerId`, `workspaceId`, `title`, `summary` (empty means unavailable), `revision`, `updatedAt`, `lifecycle`, `health`, `attention`, and `actions`. Other SDK fields may be retained but are not interpreted. This projection validator is not full SDK schema validation. Null/unselected workspaces are excluded, not silently assigned. Future timestamps and duplicate provider-scoped identities fail. One-MiB input limit; bounded arrays.

For this read-only local observation projection, every provider must have `capabilities.control: []` and every work item must have `actions: []`. The helper rejects advertised controls. Supplied records are not authenticated observations.

Full SDK snapshots can be supplied; unused actors, attempts, artifacts, evidence and attention entities are not summarized by these helpers. Work-item summary/attention is a bounded overview, not a complete transcript or approval queue. Minimize export content before sending it to an AI host. Do not paste private credentials.

Daily Brief additionally requires timezone-aware `since`, not later than assessmentTime. Optional `previousSnapshot` uses the same projection and scope; it must precede the current snapshot and be at or before `since`. Without it, label first observations baseline_unavailable, not new work or completed today. The helper compares revision, title, summary, lifecycle, attention and health; it records whether the latest supplied updatedAt falls in the window, without claiming when each change occurred. Missing work becomes not_observed_now. It does not read secrets, previous private reports, external sources or model transcripts automatically.

The scoped exporter can explicitly label null source workspace IDs for local review using --unassigned-workspace. It retains sourceWorkspaceId:null and exportMetadata; the label does not establish source workspace membership. No silent assignment is performed.
