import sys, cv2, datetime, base64, time
import os
import data
from PyQt4 import QtCore, QtGui
from scanwindow import Ui_Form

# TODO: Split files to maximum 250mb or less
# TODO: Add camera selection to combobox
# TODO: Add delay between camera.read operations
# TODO: Test FRAMERATE of camera, round up, and use this to set camera read delay
# TODO: for camera delay, use a timer ?
# TODO: Add hot keys for buttons
# TODO: Change format for records
# TODO: Query UPC DB online for unique bar codes
# TODO: Add tests!

class CameraThread(QtCore.QThread):
    imgSaved = QtCore.pyqtSignal(str)
    camReady = QtCore.pyqtSignal()

    def __init__(self, camera_port=0):
        QtCore.QThread.__init__(self)
        self.camera_port = camera_port
        self.camera = None
        self.openCamera(camera_port)
        self.camera.set(3, 1600) # width
        self.camera.set(4, 1200) # height
        self.height = self.camera.get(4)
        self.width = self.camera.get(3)
        self.fps = self.getfps()
        self.last_image = None
        self.active = True

    def __del__(self):
        self.active = False
        self.wait()
        if self.isRunning():
            self.closeCamera()

    def run(self):
        while(self.active):
            retval, self.last_image = self.camera.read()
            self.camReady.emit()

    def getfps(self):
        """Returns the FPS of the opened camera"""
        num_frames = 15
        start = time.time()
        for i in range(0, num_frames):
            self.camera.read()
        end = time.time()
        seconds = end - start
        fps = num_frames / seconds
        return fps

    def save(self, image_file):
        """Save image to disk"""
        cv2.imwrite(image_file, self.last_image)
        self.imgSaved.emit(image_file)

    def isRunning(self):
        """Returns true if the camera object is active"""
        return self.camera.isOpened()

    def openCamera(self, port=0):
        """Opens a camera by port"""
        self.camera = cv2.VideoCapture(port)
        #Following may be required for some cameras
        if not self.isRunning():
            self.camera.open()

    def closeCamera(self):
        """Deactivates the camera"""
        self.camera.release()

    def read(self):
        """Gets a frame from the camera"""
        return self.camera.read() # Returnvalue, PILImage

class StartScan(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.db = data.LocalData()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.btnTakePhoto.clicked.connect(self.snapshot)
        self.ui.btnWrite.clicked.connect(self.writeout)
        self.ui.btnRefreshCameras.clicked.connect(self.refreshCameras)
        self.ui.cmbCamera.currentIndexChanged.connect(self.changeCamera)
        self.ui.txtInput.returnPressed.connect(self.getinput)
        self.camera_port = 0
        self.camera = CameraThread(self.camera_port)
        self.camera.camReady.connect(self.updateLiveView)
        self.camera.imgSaved.connect(self.updatePreview)
        self.camera.start()
        self.last_text = None
        self.last_image = None
        self.image_folder = "./img/"
        os.makedirs(self.image_folder, exist_ok=True)
        self.saved_image_format = ".jpg"
        self.live_image_format = ".jpg"
        #self.data_file = "./" + datetime.datetime.now().strftime('%Y%m%d.%H%M%S') + '.csv'
        self.record_count = 0
        #fw = open(self.data_file, "w")
        #fw.write("ID,TimeStamp,UPC,PNGImage(Base64)\n")
        #fw.close()
        #self.refreshCameras()

    def closeEvent(self, QCloseEvent):
        """Gracefully shutdown the camera"""
        self.camera.active = False
        #Delay 1 frame to allow camera to finish any in-process frame grabs
        time.sleep(1 / self.camera.fps)
        self.camera.closeCamera()

    def changeCamera(self, port=0):
        """Selects and opens a new camera for input"""
        pass

    def snapshot(self, id):
        """Gets a frame from the camera and returns its path"""
        self.last_image = self.image_folder + \
                     id + \
                     '-' + \
                     str(time.time()) + \
                     self.saved_image_format
        self.camera.save(self.last_image)
        self.ui.txtInput.setFocus()
        return self.last_image

    def updateLiveView(self):
        """Updates the live camera view"""
        retval, img = cv2.imencode(self.live_image_format, self.camera.last_image)
        im = QtGui.QImage.fromData(img)
        pix = QtGui.QPixmap(im)
        self.ui.lblLiveView.setPixmap(pix)

    def updatePreview(self, image_file):
        """Updates the preview window of the last image written"""
        pix = QtGui.QPixmap(image_file)
        pix = pix.scaled(self.ui.lblPreview.size(), QtCore.Qt.KeepAspectRatio)
        self.ui.lblPreview.setPixmap(pix)

    def refreshCameras(self):
        """Gets the available cameras and populates the combo box"""
        current_camera = 0
        if self.camera.isRunning():
            current_camera = self.camera.camera_port
            self.camera.exit()
        for i in range(10, 0, -1):
            self.camera.camera = cv2.VideoCapture(i)
            if self.camera.isRunning():
                self.ui.cmbCamera.clear()
                for y in range(i, -1, -1):
                    self.ui.cmbCamera.addItem(str(y), y)
        if self.camera.camera.isRunning() == False:
            self.camera.openCamera(current_camera)

    def writeout(self):
        """Writes a record to the data file"""
        if self.last_image == None:
            self.last_image = ""
        if self.last_text != None:
            #f = open(self.image_file + self.saved_image_format, "rb").read()
            #fw = open(self.data_file, "a")
            self.db.put_row(self.last_text, self.last_image)
            self.db.do_commit()
            #fw.write(str(self.record_count) +
            #         ',' +
            #         str(datetime.datetime.now()) +
            #         ',' +
            #         self.last_text +
            #         ',' +
            #         base64.b64encode(f).decode() +
            #         '\n')
            #fw.close()
            self.last_text = None
            self.record_count += 1
            self.ui.txtInput.setFocus()

    def getinput(self):
        """Takes the input from the input box"""
        self.writeout()
        if self.ui.txtInput.text() != "":
            self.last_text = self.ui.txtInput.text()
            self.snapshot(self.last_text)
            self.ui.txtHistory.setPlainText(str(self.record_count) +
                                            ": " +
                                            self.last_text +
                                            "\n" +
                                            self.ui.txtHistory.toPlainText())
            self.ui.txtInput.setText("")
        else:
            self.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartScan()
    myapp.show()
    sys.exit(app.exec_())
