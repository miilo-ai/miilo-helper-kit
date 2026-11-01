# Output contract

Miilo observes coding agents locally, read-only, with no control actions. Miilo Control only reviews action records you supply and never runs them.

`review.json`, `review.md`, `work.csv`, `action-review.csv`. Review states: unmatched_target, needs_evidence, record_review, recorded_complete, reconcile. Every JSON action record and every CSV/Markdown action row has dispatchAllowed=false. record_review means only that a supplied record matches the observation; recorded_complete refers only to a supplied receipt, not verified execution.

Reports are based on supplied data; redaction is best effort. Review before sharing. A zero helper exit status does not verify source authenticity or outcomes.

When no action records are supplied, show the selected observation context and explicitly state that there are no records to audit. Do not invent request/receipt records or infer action outcomes. The JSON report includes observations, recordCount and top-level dispatchAllowed=false.
