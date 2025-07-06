"""
Pytest configuration for Jupiter Ultra MCP Server tests.
"""

from typing import Any

import pytest


def pytest_configure(config: Any) -> None:  # type: ignore[misc]
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "paid: mark test as requiring actual SOL (paid test)"
    )


def pytest_collection_modifyitems(config: Any, items: Any) -> None:  # type: ignore[misc]
    """Modify test collection based on command line options."""
    if not config.getoption("--run-paid-tests"):
        # Skip paid tests unless explicitly requested
        skip_paid = pytest.mark.skip(reason="need --run-paid-tests option to run")
        for item in items:
            if "paid" in item.keywords:
                item.add_marker(skip_paid)


def pytest_addoption(parser: Any) -> None:  # type: ignore[misc]
    """Add custom command line options."""
    parser.addoption(
        "--run-paid-tests",
        action="store_true",
        default=False,
        help="run paid tests that require actual SOL",
    )
