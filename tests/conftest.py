"""Shared test setup for a clean repository checkout."""

import pytest

from src.h2s_dataset_builder import main as build_h2s_datasets


@pytest.fixture(scope="session", autouse=True)
def generate_h2s_evidence_layer():
    """Build generated H2S datasets before tests inspect or analyze them."""

    build_h2s_datasets()
