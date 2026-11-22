# Configuration layout

`config.yaml` composes the environment, robot, agent, and experiment groups.
The files are plain YAML so they can be read by Hydra or a lightweight loader
in CPU-only development environments. Values follow SI units internally.

The `fitted/` directory contains validation-only parameter artifacts. The
`splits/` directory is immutable after a split manifest is published.
