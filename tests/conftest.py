from pytest_easy import TestFilesHandler

import pytest


TESTS_LOG_FILENAME = 'test_files/tests.log'

@pytest.fixture(scope = 'session', autouse = True)
def setup_and_teardown_session(
    request
):
    """
    Method to remove the folder for temporary files when
    the testing process has finished.
    """
    from printer_easy import ConsolePrinter

    # Code to run at the begining
    ConsolePrinter().deactivate_print()
    # ConsolePrinter().activate_print()
    test_files_handler = TestFilesHandler()

    yield
    
    # Code to run after all tests have finished
    test_files_handler.delete_new_files()