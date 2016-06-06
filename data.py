import sqlite3
import arrow
import os

class LocalData():

    def __init__(self, data_file: str='./data.db'):
        self.data_file = data_file
        self.conn = None
        self.cur = None
        self.rows = None

    def __del__(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()

    def open_database(self, data_file: str='') -> bool:
        """
        :param data_file: str
        :return: bool
        Connects to a database file if it exists
        Creates new database if it doesn't exist
        Returns True if successfully connected
        Returns False otherwise
        """
        if data_file == '':
            if self.data_file == '': return False
        else:
            self.data_file = data_file
        # if database doesn't exist, create it
        if not os.path.exists(self.data_file):
            if not self.create_database(self.data_file): return False
        self.rows = None
        self.conn = sqlite3.connect(self.data_file)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        return True

    def create_database(self, data_file: str='') -> bool:
        """
        :param data_file: str
        :return: bool
        Creates a database with the correct structure.
        Returns True if database is successfully created
        Returns False if database already exists or could not be created
        """
        if data_file == '':
            if self.data_file == '':
                return False
            else:
                data_file = self.data_file
        if os.path.exists(data_file): return False
        conn = sqlite3.connect(data_file)
        schema = open('./sql/schema.sql', mode='r').read()
        conn.executescript(schema)
        conn.commit()
        conn.close()
        if os.path.exists(data_file):
            return True
        else:
            return False

    def get_rows(self):
        """Gets all data from the database and fills the rows variable"""
        self.cur.execute('SELECT barcode_id, img_file, date_time, ROWID '
                         'FROM tblInventory')
        self.rows = self.cur.fetchall()
        return self.rows

    def get_rows_by_barcode(self, barcode_id):
        """Returns all rows matching a barcode_id"""
        self.cur.execute('SELECT * FROM tblInventory WHERE barcode_id=?', (barcode_id))
        self.rows = self.cur.fetchall()
        return self.rows

    def get_row_by_id(self, row_id):
        """Returns a single row from the database"""
        self.cur.execute('SELECT * FROM tblInventory WHERE ROWID = ?', (row_id))
        return self.cur.fetchone()

    def put_row(self, barcode_id, img_file, date_time=arrow.now('local')):
        """Adds a new row into the database"""
        self.cur.execute('INSERT INTO tblInventory ('
                         'date_time, '
                         'barcode_id, '
                         'img_file) '
                         'VALUES(?,?,?)',
                         (str(date_time),
                          str(barcode_id),
                          str(img_file)))

    def delete_row_by_id(self, row_id):
        """Deletes a single row from the database"""
        self.cur.execute('DELETE FROM tblInventory WHERE ROWID = ?', (row_id))

    def delete_rows_by_barcode(self, barcode_id):
        """Deletes all rows matching a barcode_id"""
        self.cur.execute('DELETE FROM tblInventory WHERE barcode_id = ?', (barcode_id))

    def do_commit(self):
        """Write data to disk"""
        self.conn.commit()

    def update_row_by_id(self, row_id, barcode_id=None, img_file=None, date_time=None):
        """Updates a single row by its ID"""
        temp_row = self.get_row_by_id(row_id)
        if barcode_id == None:
            barcode_id = temp_row['barcode_id']
        if img_file == None:
            img_file = temp_row['img_file']
        if date_time == None:
            date_time = temp_row['date_time']
        self.cur.execute('UPDATE tblInventory SET barcode_id=?,'
                         'img_file=?,'
                         'date_time=? '
                         'WHERE ROWID=?',
                         (barcode_id, img_file, str(date_time), row_id))
