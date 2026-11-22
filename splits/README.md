# Data splits

Split manifests are keyed by scene source and generation parameters. A scene
identifier may occur in exactly one split. The test split is only readable by
evaluation commands that set `ALLOW_TEST=1` explicitly.

The initial repository ships a tiny synthetic manifest for smoke tests. It is
not a paper-scale benchmark and should be replaced by the S0.4 scene manifest
before running final experiments.
