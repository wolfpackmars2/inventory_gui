# inventory_gui
PyQt4 GUI for mass importing retail product into a database.

The Purpose of the GUI is to facilitate mass import of UPC and product image data, which will form the basis for a product database.

## Requires
- OpenCV 3
- PyQt4
- SIP
- Python 3.4+

#### Version 0.0.2
- Initial working version

When text is entered into the input box, an attached webcam will snap a photo and the data entered into the input will be stored in memory. In practice, a retail or other item that you want to add to the data base is positioned in front of the camera and its barcode is read with a barcode scanner.  A CSV file is generated, which contains the text from the input box (ie - barcode digits), timestamp, and the jpg image encoded as a Base64 string.

Future versions will store data in a database (either local or remote, haven't decided yet) and integrate with a web app.
