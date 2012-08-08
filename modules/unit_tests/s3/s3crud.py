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

        current.auth.override = True
        resource = current.manager.define_resource("project", "project")

        # insert something that creates a CRUD instance?
        resource_form = crud.form(resource=resource)
        factory_form = SQLFORM.factory(db.project_project)

        self.assertEqual(factory_form, resource_form)

    def testCreateFormFromRecord(self):
        """
            Generate an "update" form from a record
        """

        current.auth.override = True
        resource = current.manager.define_resource("project", "project", id=1)
        request = current.manager.parse_request("project", "project")

        crud = s3.s3crud.S3CRUD(

        resource.crud(self, method="_init")

        #~ root = tree.getroot()
        #~ self.assertEqual(root.tag, xml.TAG.root)

        #~ attrib = root.attrib
        #~ self.assertEqual(len(attrib), 5)
        #~ self.assertEqual(attrib["success"], "true")
        #~ self.assertEqual(attrib["start"], "0")
        #~ self.assertEqual(attrib["limit"], "1")
        #~ self.assertEqual(attrib["results"], "1")
        #~ self.assertTrue("url" in attrib)

        #~ self.assertEqual(len(root), 1)
        #~ for child in root:
            #~ self.assertEqual(child.tag, xml.TAG.resource)
            #~ attrib = child.attrib
            #~ self.assertEqual(attrib["name"], "org_office")
            #~ self.assertTrue("uuid" in attrib)

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
