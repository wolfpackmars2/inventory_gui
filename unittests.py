import unittest
import data, scan, Util
import sys, os, uuid
from PyQt4 import QtCore, QtGui

# ToDo: open_database should close previous db before opening a new db
# ToDo: open_database should raise a FileNotExists error when opening nonexistent db
# ToDo: open_database should raise BadFileError when opening non-db file
# ToDo: write test for close_database
# ToDo: write test for create_database
# ToDo: write test for destroy_database
# ToDo: StartScan should only start camera when requested to do so
# ToDo: camera tests
# ToDo: test start_livecam
# ToDo: make file name testing more extensive - ie test on different OS

# User should be able to create a new database
# User should be able to open an existing database
# When opening database, any previous database should be closed
# User should be able to close database ?
# App should have limited functionality if a database isn't open
# User should be able to import and export data from the database

class ScanFunctionsTests(unittest.TestCase):
    test_database = str(uuid.uuid4()) + '.test1.db'
    alt_database = str(uuid.uuid4()) + '.test2.db'

    def setUp(self):
        # For now, we will need to open the GUI to perform tests
        self.app = QtGui.QApplication(sys.argv)

        self.ss = scan.StartScan()
        self.ss.showMinimized()
        # ToDo: set up test database

    def tearDown(self):
        # sys.exit(self.app.exec_())
        # Clean up created files
        if os.path.exists(self.test_database):
            os.remove(self.test_database)
        if os.path.exists(self.alt_database):
            os.remove(self.alt_database)

    def test_create_database(self):
        """Should return true if db can be created"""
        self.assertTrue(self.ss.create_database(self.test_database),
                        "Create testing database")
        self.assertTrue(os.path.exists(self.test_database))
        self.assertNotEqual(self.test_database, self.ss.data_file(),
                            "Should not connect to created database")

    def test_open_database(self):
        """Should return true to open database"""
        self.assertTrue(self.ss.open_database(self.test_database))
        self.assertEqual(self.ss.data_file(), self.test_database)
        self.assertTrue(os.path.exists(self.test_database))
        # database should be created if it doesn't exist
        self.assertTrue(self.ss.open_database(self.alt_database))
        self.assertEqual(self.ss.data_file(), self.alt_database)
        self.assertTrue(os.path.exists(self.alt_database))

    def test_close_database(self):
        """Test close_database"""
        if self.ss.db is None:
            # Can't test close_database if no database is open
            self.ss.open_database(self.test_database)
        self.ss.close_database()
        # data_file should be None
        self.assertEqual(self.ss.data_file(), '')
        self.assertIsNone(self.ss.db)


class UtilTests(unittest.TestCase):

    def test_valid_pathname(self):
        """Should return true for valid path"""
        self.assertTrue(Util.is_pathname_valid('./myrandomvalidfilename.dat'))
        self.assertTrue(Util.is_pathname_valid('myrandomvalidfilename.dat'))

    def test_invalid_pathname(self):
        """Should return false for invalid path"""
        self.assertFalse(Util.is_pathname_valid(''))

if __name__ == '__main__':
    unittest.main()