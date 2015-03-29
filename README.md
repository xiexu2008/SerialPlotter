# SerialPlotter
The repository contains a python script "PlotSerialPort.py" which can be used to plot a serial port. It supports plotting data with arbitrary dimensions. Users indicate the serial COM port and the dimensions of the serial data. The example below is to plot serial port whose data is three dimensions.

python PlotSerialPort.py --port /dev/tty.usbmodem1411 --dimension 3

Also make sure the serial data is formated in this way "X1,X2,...,Xk\n", where k is the dimension and the X1 to Xk are the dimension data.

The scriplt also contains a function "TestAnimationWithFakeStream". It allows you to see how the plotting goes without a real seral COM port.
