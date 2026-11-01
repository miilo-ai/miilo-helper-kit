# Input contract

This kit accepts a **local review envelope**, not a new Miilo API or SDK replacement. Supply `assessmentTime` (timezone-aware), `maxAgeSeconds` (integer 1–3600), and explicit `scope.providerIds` and `scope.workspaceIds` arrays. No wildcard or inferred workspace expansion. A work item's identity is `(providerId, id)`; matching titles and reused IDs across providers are not interchangeable.

`snapshot` is a supplied projection of the Miilo protocol 0.1 camelCase snapshot: `protocolVersion`, `snapshotId`, `observedAt`, `providers`, `workItems`. Providers need `id`, `health`, `capabilities.control`. Work items need `id`, `providerId`, `workspaceId`, `title`, `summary` (empty means unavailable), `revision`, `updatedAt`, `lifecycle`, `health`, `attention`, and `actions`. Other SDK fields may be retained but are not interpreted. This projection validator is not full SDK schema validation. Null/unselected workspaces are excluded, not silently assigned. Future timestamps and duplicate provider-scoped identities fail. One-MiB input limit; bounded arrays.

For this read-only local observation projection, every provider must have `capabilities.control: []` and every work item must have `actions: []`. The helper rejects advertised controls. Supplied records are not authenticated observations.

Full SDK snapshots can be supplied; unused actors, attempts, artifacts, evidence and attention entities are not summarized by these helpers. Work-item summary/attention is a bounded overview, not a complete transcript or approval queue. Minimize export content before sending it to an AI host. Do not paste private credentials.

Control adds required arrays `requests` (max 100) and `receipts` (max 1000). These are external action records supplied by the user for review, not actions exposed by Miilo. Each request has unique `id`, `providerId`, `workId`, `actionId`, `expectedRevision`, `recordSource`, and bounded `input` object. Each receipt has `requestId`, `providerId`, `actionId`, `status`, `recordedAt`, `recordSource`. Status may be accepted/completed/rejected/failed/conflict/unknown. The unknown marker belongs to this review envelope. Record sources are labels, not fetched URLs.

The helper matches records to selected observations, compares revisions, hashes supplied arguments and reports unresolved/conflicting outcomes. It does not validate an action input schema, grant permission, issue confirmations or execute anything. Supplied records do not confer permission.

The scoped exporter can explicitly label null source workspace IDs for local review using --unassigned-workspace. It retains sourceWorkspaceId:null and exportMetadata; the label does not establish source workspace membership. No silent assignment is performed.
