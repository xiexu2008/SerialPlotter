# SerialPlotter
The repository contains a python script "PlotSerialPort.py" which can be used to plot a serial port. It supports plotting data with arbitrary dimensions. Users specify the serial COM port and the dimensions of the serial data. The example below is to plot serial port whose data is three dimensions.

python PlotSerialPort.py --port /dev/tty.usbmodem1411 --dimension 3

Also make sure the serial data is formated in this way "X1,X2,...,Xk\n", where k is the dimension, the X1 to Xk are the dimension data, and the \n is the newline indicating the end of the data.

The scriplt also has a function "TestAnimationWithFakeStream". It allows you to see how the plotting goes without a real seral COM port.
