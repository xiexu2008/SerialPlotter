"""
PlotSerialPort.py

The script supports plotting data with arbitrary dimensions. Users specify the serial COM port and the
dimensions of the serial data. The example below is to plot serial port whose data is three dimensions.

python PlotSerialPort.py --port /dev/tty.usbmodem1411 --dimension 3

Also make sure the serial data is formated in this way "X1,X2,...,Xk\n", where k is the dimension,
the X1 to Xk are the dimension data, and the \n is the newline indicating the end of the data.

The script also has a function "TestAnimationWithFakeStream". It allows you to see how the plotting goes
without a real seral COM port.

References:
http://www.laurentluce.com/posts/python-threads-synchronization-locks-rlocks-semaphores-conditions-events-and-queues/
http://electronut.in/

"""

import random
import serial, argparse
import threading
import time
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re


class PlotDataProducer:

    def __init__(self, plotDataBuffer, bufferSyncCondition, dataInStream):
        self.plotDataBuffer = plotDataBuffer
        self.bufferSyncCondition = bufferSyncCondition
        self.dataInStream = dataInStream

    def ProducePlotData(self):
        line = ""
        while True:
            ch = self.dataInStream.read(1)
            if ch != '\n':
                line += ch
            elif line:
                self.bufferSyncCondition.acquire()
                self.plotDataBuffer.append(line)
                self.bufferSyncCondition.notify()
                self.bufferSyncCondition.release()
                line = ""
                time.sleep(0.01)  # 10 ms


class PlotDataConsumer:

    def __init__(self, plotDataBuffer, bufferSyncCondition):
        self.plotDataBuffer = plotDataBuffer
        self.bufferSyncCondition = bufferSyncCondition

    def GetPlotData(self):
        self.bufferSyncCondition.acquire()
        lineStr = ""
        while True:
            if self.plotDataBuffer:
                lineStr = self.plotDataBuffer.popleft()
                break
            self.bufferSyncCondition.wait()
        self.bufferSyncCondition.release()

        return lineStr


class Animator:

    def __init__(self, plotDataSource, numOfPlots, maxLengthOfPlotBuffer):
        self.plotDataSource = plotDataSource
        self.numOfPlots = numOfPlots
        self.maxLengthOfPlotBuffer = maxLengthOfPlotBuffer
        # make a list of queues and initialize it with 0.0
        self.dataBufferByPlot = [deque([0.0]*self.maxLengthOfPlotBuffer, maxlen=maxLengthOfPlotBuffer) for i in range(self.numOfPlots)]

        # set up animation
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, maxLengthOfPlotBuffer), ylim=(-500, 500))
        self.plots = [self.ax.plot([], [])[0] for i in range(self.numOfPlots)]


    def Animate(self):
        anim = animation.FuncAnimation(self.fig, self.UpdatePlotData, interval=10)  # interval unit: ms
        plt.show()


    def UpdatePlotData(self, frames):
        try:
            dataStr = self.plotDataSource.GetPlotData()
            print dataStr
            plotData = [float(val) for val in dataStr.split(",") if re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)', val, re.DOTALL)]
            if len(plotData) == self.numOfPlots:
                self.AddToPlotBuffer(plotData)
                for i in range(self.numOfPlots):
                    self.plots[i].set_data(range(self.maxLengthOfPlotBuffer), self.dataBufferByPlot[i])

        except KeyboardInterrupt:
            print "exiting"

        return self.plots[0]


    def AddToPlotBuffer(self, plotData):
        for i in range(len(plotData)):
            self.dataBufferByPlot[i].appendleft(plotData[i])


def DoAnimation(sourceDataStream, sourceDataDimension):

    plotDataBuffer = deque()
    synCondition = threading.Condition()
    producer = PlotDataProducer(plotDataBuffer, synCondition, sourceDataStream)
    consumer = PlotDataConsumer(plotDataBuffer, synCondition)

    thrdProducer = threading.Thread(target=producer.ProducePlotData)
    thrdProducer.start()

    maxLengthPlotBuffer = 200
    animator = Animator(consumer, sourceDataDimension, maxLengthPlotBuffer)
    animator.Animate()


def AnimateSerialPort(serialPort, dataDimension):

    baudRate = 9600
    ser = serial.Serial(serialPort, baudRate)
    ser.read(ser.inWaiting())   # empty the receiving buffer
    DoAnimation(ser, dataDimension)

    if ser:
        ser.close()


# for testing
class TestDataInStream:

    # constructor
    def __init__(self, dataDimensions):
        self.dataDimensions = dataDimensions
        self.buffer = deque()

    def read(self, numOfCharsToRead):
        if not self.buffer or len(self.buffer) < numOfCharsToRead:
            self.MakeDigits()
        return "".join([self.buffer.popleft() for i in range(numOfCharsToRead)])

    def MakeDigits(self):
        line = ",".join([str(random.randint(-256, 256)) for i in range(self.dataDimensions)]) + "\n"
        for ch in line:
            self.buffer.append(ch)
        return line

# for testing
def TestAnimationWithFakeStream():

    numOfDataChannels = 3
    sourceStream = TestDataInStream(numOfDataChannels)
    DoAnimation(sourceStream, numOfDataChannels)


def main():
    # python PlotSerialPort.py --port /dev/tty.usbmodem1411 --dimension 3
    parser = argparse.ArgumentParser(description="plot serial")
    parser.add_argument("--port", dest="port", required="True")
    parser.add_argument("--dimension", dest="dimension", required="True")

    args = parser.parse_args()
    strPort = args.port
    dataDimension = int(args.dimension)
    AnimateSerialPort(strPort, dataDimension)


if __name__ == "__main__":

    #TestAnimationWithFakeStream()
    main()
