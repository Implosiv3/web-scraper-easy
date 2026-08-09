"""
A simple test to verify that pytes is working and
the tests are being detected.
"""
import pytest


@pytest.mark.mandatory
def test_mandatory():
    assert True

@pytest.mark.additional
def test_additional():
    assert True