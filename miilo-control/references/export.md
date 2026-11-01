# Obtain a local observation export

Miilo's local observer is not Linux-only. The installed macOS CLI 0.4.0 exposes `miilo local snapshot`; Linux is checked separately in the repository's qualification evidence. These instructions concern read-only local observations, not a server or control connection. Do not assume Windows support was tested.

The underlying command is `miilo local snapshot`. It reads the existing configured selection and prints JSON; it does not enroll sessions, start agent work or install anything. An existing healthy collector is required. If the snapshot is stale/unavailable, inspect `miilo local doctor` and the installed `miilo local --help`. The owner may run their existing configured observer with `miilo local run` in another terminal; this kit never starts it automatically. If the command is absent, stop and check the installed version rather than guessing file paths or searching a buyer's computer.

## Select and minimize

From this product's helper folder, list IDs without titles or summaries:

```sh
python3 scripts/export.py --capture-local --list
```

Choose the exact IDs to include, then prepare a private local review input:

```sh
python3 scripts/export.py --capture-local --provider-id 'PROVIDER_ID_FROM_LIST' --workspace-id 'WORKSPACE_ID_FROM_LIST'  --output /tmp/miilo-review-input
python3 scripts/workflow.py /tmp/miilo-review-input/input.json /tmp/miilo-review-report
```

Replace the IDs and (for Brief) the window start with the owner's actual choices; do not run literal placeholders. Repeat --provider-id/--workspace-id for multiple explicit selections. Use a fresh output directory each time. `--assessment-time` is optional and defaults to current UTC; `--max-age-seconds` defaults to 60 (allowed 1–3600). For Control, pass `--records records.json` containing the supplied requests/receipts; without it the arrays are empty.

If the list reports `hasUnassignedWork: true`, some source work has a null workspace ID. Do not invent source membership. To include that work intentionally, choose a local review label and pass both `--workspace-id personal-review --unassigned-workspace personal-review`. The export marks `sourceWorkspaceId: null` and records the alias in exportMetadata. This label belongs only to the review and does not create or rename a Miilo workspace.

## Supplied file or helper-free bot

Instead of capture, use `--snapshot /path/to/supplied-snapshot.json`; `--snapshot` and `--capture-local` are mutually exclusive. No model or network request is made by the Python helper; capture invokes only the existing `miilo local snapshot` command once. It does not fetch URLs or read configuration/credentials itself.

The exporter retains only the selected providers and bounded work projection, excluding actors, transcripts, artifacts and arbitrary extensions. Output directories/files are private (0700/0600). Summaries can still be sensitive; automated redaction is best effort. Review input.json locally before attaching it to Grok or another host. Export creation itself uploads nothing.

A Grok template cannot bundle these Python files. Its first conversation should ask for the selected, minimized export or guide the owner through the helper kit. Without helpers, perform a clearly labeled manual review and do not claim executable checks ran. Never search a buyer's computer until they identify/authorize the source. If no export exists yet, explain setup; do not present the synthetic example as their live brief.
