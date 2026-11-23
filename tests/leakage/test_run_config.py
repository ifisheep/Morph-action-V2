"""Tests for explicit test-split opt-in."""

from __future__ import annotations

import pytest

from morphdream.decision.loop import RunConfig


def test_test_split_requires_environment_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLOW_TEST", raising=False)

    with pytest.raises(PermissionError, match="ALLOW_TEST=1"):
        RunConfig(split="test")


def test_test_split_accepts_environment_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_TEST", "1")

    assert RunConfig(split="test").split == "test"
