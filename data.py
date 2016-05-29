import sqlite3
import time
import datetime
import base64
import os
import csv
import arrow

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
                          'date_time TEXT, '
                          'barcode_id TEXT,'
                          'img_file TEXT)')

    def get_rows(self):
        """Gets all data from the database and fills the rows variable"""
        self.cur.execute('SELECT barcode_id, img_file, date_time, ROWID '
                         'FROM tblInventory')
        self.rows = self.cur.fetchall()
        return self.rows

    def put_row(self, barcode_id, img_file, date_time=arrow.now('local')):
        """Adds a new row into the database"""
        print(str(barcode_id))
        print(str(img_file))
        print(str(date_time))
        self.cur.execute('INSERT INTO tblInventory ('
                         'date_time, '
                         'barcode_id, '
                         'img_file) '
                         'VALUES(?,?,?)',
                         (str(date_time),
                          str(barcode_id),
                          img_file))

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
        print(self.data_file + " closed")

class CSV_Data():
    def __init__(self, csv_file = None, db_file = None):
        if csv_file == None:
            csv_file = "./" + datetime.datetime.now().strftime('%Y%m%d.%H%M%S') + ".csv"
        if db_file == None:
            db_file = './data.db'
        self.db_file = db_file
        self.csv_file = csv_file
        self.record_count = 0

    def export_to_csv(self, csv_file = None, db_file = None):
        """Exports data to CSV"""
        if csv_file == None:
            csv_file = self.csv_file
        if db_file == None:
            db_file = self.db_file
        db = LocalData(db_file)
        fw = open(csv_file, "w", newline='')
        #fw.write("ID,TimeStamp,UPC,PNGImage(Base64)\n")
        csv_writer = csv.writer(fw)
        csv_writer.writerow('ID', 'UTCTime', 'UPC', 'Image(Base64)', 'ImagePath')
        for row in db.get_rows():
            image_file = row['img_file']
            if os.path.isfile(image_file):
                f = open(image_file, "rb").read()
                img_data = base64.b64encode(f).decode()
            else:
                img_data = ''
            csv_writer.writerow(self.record_count,
                                row['date_time'],
                                row['barcode_id'],
                                img_data,
                                row['image_file'])
            #fw.write(str(self.record_count) +
            #         ',' +
            #         str(datetime.datetime.fromtimestamp(row['date_time'])) +
            #         ',' +
            #         row['barcode_id'] +
            #         ',' +
            #         img_data +
            #         '\n')
            self.record_count += 1
        fw.close()

    def import_from_csv_002(self, csv_file = None, db_file = None):
        """Imports data from a version 0.0.2 CSV file"""
        if csv_file == None:
            csv_file = self.csv_file
        if db_file == None:
            db_file = self.db_file
        db = LocalData(db_file)
        fr = open(csv_file, "r")
        fr.readline() #skip first line (header)
        for row in fr:
            row = row.split(',')
            #2016-05-24 12:00:19.038725
            time_stamp = arrow.get(row[1])
            time_stamp = time_stamp.replace(tzinfo='US/Central')
            product_id = row[2]
            image_data = base64.b64decode(row[3])
            image_file = "./img/" + product_id + "-" + time_stamp.format('YYYYMMDD.HHmmss.SS') + ".jpg"
            #print(image_data)
            ifw = open(image_file, 'bw')
            ifw.write(image_data)
            ifw.close()
            db.put_row(product_id, image_file, time_stamp)
        #fw.write("ID,TimeStamp,UPC,PNGImage(Base64)\n")
        # csv_reader = csv.reader(fw)
        # for row in csv_reader:
        #     time_stamp = datetime.datetime.replace(row[1]).timestamp()
        #     image_file = "./img/" + row[2] + "-" + str(time_stamp) + ".jpg"
        #     print(time_stamp)
        #     print(image_file)
        #     image_data = base64.b64decode(row[3])
        #     ifw = open(image_file, 'w')
        #     ifw.write(image_data)
        #     ifw.close()
        #     db.put_row(row[2], image_file, time_stamp)

