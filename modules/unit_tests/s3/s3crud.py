# -*- coding: utf-8 -*-
#
# S3Crud Unit Tests
#
# To run this script use:
# python web2py.py -S eden -M -R applications/eden/modules/unit_tests/s3/s3crud.py
#
import unittest
import datetime
from gluon import *

# =============================================================================
class S3CrudFormTests(unittest.TestCase):

    # -------------------------------------------------------------------------
    def testCreateFormFromResource(self):
        """
            Generate a "create" form from a resource
        """
        pass

    def testCreateFormFromRecord(self):
        """
            Generate an "update" form from a record
        """
        pass

# =============================================================================
def run_suite(*test_classes):
    """ Run the test suite """

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    if suite is not None:
        unittest.TextTestRunner(verbosity=2).run(suite)
    return

if __name__ == "__main__":

    run_suite(
        S3CrudFormTests,
    )

# END ========================================================================
