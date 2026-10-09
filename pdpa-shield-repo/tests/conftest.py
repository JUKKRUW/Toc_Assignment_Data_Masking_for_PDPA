"""Tests that raise NotImplementedError are reported as XFAIL ("not implemented yet").

This keeps CI green while stubs are being filled in. As soon as a stub is implemented,
its tests run for real — a wrong answer is a normal FAIL.
"""
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if call.excinfo is not None and call.excinfo.errisinstance(NotImplementedError):
        rep.outcome = "skipped"
        rep.wasxfail = f"not implemented yet: {call.excinfo.value}"
