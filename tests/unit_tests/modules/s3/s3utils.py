# -*- coding: utf-8 -*-
#
# REST Unit Tests
#
# To run this script use:
# python web2py.py -S eden -M -R applications/eden/tests/unit_tests/modules/s3/s3utils.py
#
import unittest
from gluon.dal import Query
from s3.s3utils import *

# =============================================================================
class S3FKWrappersTests(unittest.TestCase):

    def testHasForeignKey(self):

        ptable = s3db.pr_person
        self.assertFalse(s3_has_foreign_key(ptable.first_name))
        self.assertTrue(s3_has_foreign_key(ptable.pe_id))

        htable = s3db.hrm_human_resource
        self.assertFalse(s3_has_foreign_key(htable.start_date))
        self.assertTrue(s3_has_foreign_key(htable.person_id))

        otable = s3db.org_organisation
        self.assertTrue(s3_has_foreign_key(otable.sector_id))
        self.assertFalse(s3_has_foreign_key(otable.sector_id, m2m=False))

    def testGetForeignKey(self):

        ptable = s3db.pr_person
        ktablename, key, multiple = s3_get_foreign_key(ptable.pe_id)
        self.assertEqual(ktablename, "pr_pentity")
        self.assertEqual(key, "pe_id")
        self.assertFalse(multiple)

        otable = s3db.org_organisation
        ktablename, key, multiple = s3_get_foreign_key(otable.sector_id)
        self.assertEqual(ktablename, "org_sector")
        self.assertEqual(key, "id")
        self.assertTrue(multiple)

        ktablename, key, multiple = s3_get_foreign_key(otable.sector_id, m2m=False)
        self.assertEqual(ktablename, None)
        self.assertEqual(key, None)
        self.assertEqual(multiple, None)


# =============================================================================
class S3SQLTableTests(unittest.TestCase):

    def testHTML(self):
        cols = [{'name': 'col_1', 'label': 'Col 1'}]
        table = S3SQLTable(cols,
                           rows=[[u'Val 1']])

        self.assertEqual(str(table.xml()),
                         str(TABLE(THEAD(TR(TH("Col 1", _scope="col"))),
                                   TBODY(TR(TD("Val 1"))))))

        cols = [{'name': 'id', 'label': 'Id'},
                {'name': 'col_1', 'label': 'Col 1'}]
        row_actions = [{"label": T("Activate"),
                        "url": URL(f="schedule_parser",
                                   args="[id]"),
                        "restrict": [1,]}]
        bulk_actions = [("delete", "Delete")]
        table = S3SQLTable(cols=cols[:],
                           rows=[[u'1', u'Val 1'], [u'2', u'Val 2']],
                           bulk_actions=bulk_actions)
        self.assertEqual(str(table.xml()),
                         str(FORM(SELECT(OPTION("", _value=""),
                                         OPTION("Delete", _value="delete"),
                                         _name="action"),
                                  INPUT(_type="submit", _value=T("Go")),
                                  TABLE(THEAD(TR(TH("Id", _scope="col"),
                                                 TH("Col 1", _scope="col"))),
                                        TBODY(TR(TD("1"),
                                                 TD("Val 1")),
                                              TR(TD("2"),
                                                 TD("Val 2")))),
                                  _method="post",
                                  _action="")))

        table = S3SQLTable(cols=cols[:],
                           rows=[[u'1', u'Val 1'], [u'2', u'Val 2']],
                           row_actions=row_actions)
        self.assertEqual(str(table.xml()),
                         str(TABLE(THEAD(TR(TH("Id", _scope="col"),
                                            TH("Col 1", _scope="col"),
                                            TH(""))),
                                   TBODY(TR(TD("1"),
                                            TD("Val 1"),
                                            TD("")),
                                         TR(TD("2"),
                                            TD("Val 2"),
                                            TD(""))))))

    def testFromResource(self):
        # need to be logged in to query resources
        auth.s3_impersonate("admin@example.com")

        r = current.manager.define_resource("org", "organisation")
        table = S3SQLTable.from_resource(r,
                                         ["id"],
                                         limit=1)
        self.assertEqual(table.cols,
                         [{'name': 'id', 'label': 'Id', 'type': 'id'}])
        self.assertEqual(table.rows,
                         [[u'1',]])

        # column label
        table = S3SQLTable.from_resource(r,
                                         [("MyCol", "id"),],
                                         limit=1)
        self.assertTrue(len(table.cols) == 1)
        self.assertTrue(len(table.rows) == 1)
        self.assertTrue(len(table.rows[0]) == 1)


# =============================================================================
class S3DataTableTests(unittest.TestCase):

    def testFromResource(self):
        # need to be logged in to query resources
        auth.s3_impersonate("admin@example.com")

        r = current.manager.define_resource("org", "organisation")

        # limit
        table = S3DataTable.from_resource(r,
                                          ["id"],
                                          limit=1)
        self.assertEqual(table.cols,
                         [{'name': 'id', 'label': 'Id', 'type': 'id'}])
        self.assertEqual(table.rows,
                         [[u'1',]])

        # ajax source and page_size
        table = S3DataTable.from_resource(r,
                                          ["id"],
                                          options={"sAjaxSource": "_"},
                                          page_size=1)
        self.assertEqual(table.rows, [[u'1',]])

        # ajax source, page_size and limit
        table = S3DataTable.from_resource(r,
                                          ["id"],
                                          options={"sAjaxSource": "_"},
                                          page_size=1,
                                          limit=2)
        self.assertTrue(len(table.rows) == 1)

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
        S3FKWrappersTests,
        S3SQLTableTests,
        S3DataTableTests,
    )

# END ========================================================================
