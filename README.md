# Miilo helper kit

Version 0.1.1. Two read-only local review helpers for selected Miilo observations.
Python 3.11+; standard library only. No installation or API key required to run
the synthetic examples. These helpers never execute agent actions or upload data.

## Start here

Download the versioned ZIP and SHA256SUMS from the
[v0.1.1 release](https://github.com/miilo-ai/miilo-helper-kit/releases/tag/v0.1.1).
Verify the ZIP with `shasum -a 256 -c SHA256SUMS` (macOS) or
`sha256sum -c SHA256SUMS` (Linux), then extract it.

- [Miilo Control](miilo-control/README.md): review observed work and supplied action records.
- [Miilo Daily Brief](miilo-daily-brief/README.md): summarize attention, changes and coverage gaps.

Each folder contains a synthetic example and an explicit input/output contract.
For real observations, install Miilo separately and use your existing configured
observer. Select provider/workspace IDs explicitly and review exports before
choosing to share them with Grok or another AI host. Redaction is best effort.

No private application source, agent conversations, real observations, credentials,
machine configuration, billing logic, binaries or network services are included.
The helpers do not install collectors, schedule routines, connect accounts or
verify the authenticity of supplied records. A report is not execution permission.

## Licensing

Copyright 2026 Viratec Interactive LLC. Apache-2.0; see LICENSE and NOTICE.md.
This license covers only the original files distributed in this repository.
It does not change licensing of other products or grant Miilo trademark rights.
Upstream Miilo attribution and license text are preserved separately.

## Validation

The release ZIP is checked for manifest integrity, reproducibility and execution
from a clean extraction. Synthetic examples and scoped snapshot-to-report
roundtrips pass. Full imported-Grok behavioral qualification is not claimed.

For bugs, use this repository's issues with a synthetic reproduction. Do not
include credentials, private snapshots, work summaries or machine configuration.
