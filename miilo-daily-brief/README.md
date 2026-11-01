# Miilo Daily Brief helper kit

Version 0.1.1. Python 3.11+; standard library only. Local review helpers for
selected Miilo observations. No model account, API key or Python dependency
installation is required to run the synthetic example.

From this folder, run:

```sh
python3 scripts/workflow.py examples/input.json /tmp/miilo-daily-brief-example
```

Choose a new output directory. The example is synthetic, not your live work.
Inspect every report before sharing it. A zero exit code means files were
generated, not that sources or action outcomes were independently verified.

For real observations, you need an installed Miilo CLI and an existing healthy
configured observer. See references/export.md for explicit scope selection:

```sh
python3 scripts/export.py --capture-local --list
```

Capture invokes only `miilo local snapshot` once. These helpers do not enroll
sessions, start a collector, upload data or control agents. Without Python helpers,
any AI-host review must be labeled manual with executable checks unexecuted.

[Miilo Daily Brief Grok template](https://x.ai/bot/lODwaQuvFNIM935q8hm7t)

The template and helper kit are separate. Read-only instructions do not remove
permissions from other tools already connected to your host. Review minimized
exports locally before choosing to share them. Redaction is best effort.

See references/input.md and references/output.md for exact contracts and limits.
Control reviews supplied records only; it never executes them. Daily Brief only
summarizes supplied observations. Neither schedules work or contacts anyone.

Copyright 2026 Viratec Interactive LLC. Licensed under Apache-2.0.
See ../LICENSE and ../NOTICE.md. No trademark rights are granted.
