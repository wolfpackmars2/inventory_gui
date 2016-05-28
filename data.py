import sqlite3
import time

class LocalData():
    def __init__(self, data_file='data.db'):
        self.data_file = data_file
        self.conn = sqlite3.connect(data_file)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.rows = None
        # Set up the database tables
        self.initial_setup()

    def initial_setup(self):
        """Creates base tables if they don't exist"""
        self.conn.execute('CREATE TABLE IF NOT EXISTS tblInventory ('
                          'date_time REAL, '
                          'barcode_id TEXT,'
                          'img_file TEXT)')

    def get_rows(self):
        """Gets all data from the database and fills the rows variable"""
        self.cur.execute('SELECT barcode_id, img_file, date_time, ROWID '
                         'FROM tblInventory')
        self.rows = self.cur.fetchall()
        return self.rows

    def put_row(self, barcode_id, img_file, date_time=time.time()):
        """Adds a new row into the database"""
        self.cur.execute('INSERT INTO tblInventory ('
                         'date_time, '
                         'barcode_id, '
                         'img_file) '
                         'VALUES(?,?,?)',
                         (date_time, barcode_id, img_file))

    def do_commit(self):
        """Write data to disk"""
        self.conn.commit()

    def get_rows_bybarcode(self, barcode_id):
        """Returns all rows matching a barcode_id"""
        self.cur.execute('SELECT * FROM tblInventory WHERE barcode_id = ?', (barcode_id))
        self.rows = self.cur.fetchall()
        return self.rows

    def delete_row_byid(self, row_id):
        """Deletes a single row from the database"""
        self.cur.execute('DELETE FROM tblInventory WHERE ROWID = ?', (row_id))

    def delete_rows_bybarcode(self, barcode_id):
        """Deletes all rows matching a barcode_id"""
        self.cur.execute('DELETE FROM tblInventory WHERE barcode_id = ?', (barcode_id))

    def get_row_byid(self, row_id):
        """Returns a single row from the database"""
        self.cur.execute('SELECT * FROM tblInventory WHERE ROWID = ?', (row_id))
        return self.cur.fetchone()

    def update_row_byid(self, row_id, barcode_id=None, img_file=None, date_time=None):
        """Updates a single row by its ID"""
        temp_row = self.get_row_byid(row_id)
        if barcode_id == None:
            barcode_id = temp_row['barcode_id']
        if img_file == None:
            img_file = temp_row['img_file']
        if date_time == None:
            date_time = temp_row['date_time']
        self.cur.execute('UPDATE tblInventory SET barcode_id=?,'
                         'img_file=?,'
                         'date_time=? '
                         'WHERE ROWID = ?',
                         (barcode_id, img_file, date_time, row_id))

    def __del__(self):
        self.conn.commit()
        self.conn.close()