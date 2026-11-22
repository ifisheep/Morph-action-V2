# Fitted configuration artifacts

This directory is reserved for parameters fitted on the validation split. Each
artifact must include the validation split identifier, source code revision,
configuration hash, and a SHA-256 checksum. Test data must never be read by a
fitting command. Until a fitting run produces a checked-in artifact, the
runtime uses conservative defaults from `configs/agent/default.yaml`.
