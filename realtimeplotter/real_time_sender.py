""" @package RangeFinder
  This package contains all the classes that are used to create an instance of the GUI
  The classes dont take any input and run off of each other. Button input triggers the 
 instance of one of these classes as every class generates a new window, except the plotting 
"""
import collections, math, struct, sys, time, copy, serial
import numpy as np
from threading import Thread
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from qtpy.uic import loadUi
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QLocale, QObject, QSize, Qt, QTimer
from qtpy.QtGui import QColor, QColorConstants, QFont, QVector3D, qRgb, QPalette
from qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFontComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
    QStyleFactory,
    QStyle,
)
from qtpy.QtDatavisualization import (
    Q3DCamera,
    Q3DScatter,
    Q3DTheme,
    QAbstract3DAxis,
    QAbstract3DGraph,
    QAbstract3DSeries,
    QCustom3DItem,
    QScatter3DSeries,
    QScatterDataItem,
    QScatterDataProxy,
    QValue3DAxis,
    QValue3DAxisFormatter,
)


from helpers import GenericLayoutHelper


""" RangeFinder Class
    This class creates an instance of the rangefiner application, inclduing the layout,
    the serial connection and the plotting options. 
    Buttons on the interface allow for interaction with the board
    
    This Class subclasses the QtWidgets to create an instance
    
    Methods from this class control the user interaction.
"""


class RealTimeSender(QtWidgets.QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(RealTimeSender, self).__init__(parent)

        """
        Text and Line Edits
        """        
        self.lineedit_message = QtWidgets.QLineEdit()
        self.lineedit_message.setFixedSize(120, 50)
        
        self.textedit_output = QtWidgets.QTextEdit(readOnly=True)
        self.textedit_output.setFixedWidth(500)
    
    
        """ Timers (ms) """
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """ Buttons """
        self.button_send = QtWidgets.QPushButton(text="Send to Board", clicked=self.send)
        self.button_send.setFixedSize(120, 50)

        self.button_connect = QtWidgets.QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button_connect.setStyleSheet("background-color: red")
        self.button_connect.setFixedSize(120, 50)

        """ Layout """
        VBox = QtWidgets.QVBoxLayout(self)
        
        vbox_layout_one = QtWidgets.QVBoxLayout()
        vbox_layout_one = GenericLayoutHelper(
            QtWidgets.QVBoxLayout(), 
            [
                self.lineedit_message,
                self.button_send,
                self.button_connect,
            ]
        )
        
        hbox_layout_one = QtWidgets.QHBoxLayout()
        hbox_layout_one.addLayout(vbox_layout_one)
        
        hbox_layout_two = QtWidgets.QHBoxLayout()
        hbox_layout_two.addWidget(self.textedit_output, 1)
        
        VBox.addLayout(hbox_layout_one)
        VBox.addLayout(hbox_layout_two)
        

        self.setWindowTitle("Range Finder")
        
        """ commands """
        self.command_d = "d"
        self.command_h = "h"

        self.plotbank = []

        """ Serial Connection configuration """
        self.serial = QtSerialPort.QSerialPort(
            "COM6", 
            baudRate=QtSerialPort.QSerialPort.Baud9600, 
            readyRead=self.receive,
            
        )
        self.rng = np.random.default_rng(12345)
        self.serial.open(self.serial.ReadWrite)

    """ Method to read from serial, convert the data and send it to be plotted  """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            self.textedit_output.append(f"[Received] {raw_input_data}")
            print(f"[Received] {raw_input_data}")
            
            
            #raw_input_data = list(map(int, raw_input_data.rstrip("\r\n").split(",")))
            #theta = math.radians(raw_input_data[1])
            #phi = math.radians(raw_input_data[0])
            #distance = raw_input_data[2]
            #x_val = distance * math.sin(theta) * math.cos(phi)
            #y_val = distance * math.sin(theta) * math.sin(phi)
            #z_val = distance * math.cos(theta)
            #self.textedit_output.append(f"x = {x_val} y = {y_val} z = {z_val}")
            #self.plotbank.append(f"x = {x_val} y = {y_val} z = {z_val}")

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        # command = f'[Sent] {self.lineedit_message.text()}\r'
        phi = self.rng.integers(low=-1500, high=1500)
        dist = self.rng.integers(low=-1500, high=1500)
        theta = self.rng.integers(low=-1500, high=1500)
        
        command = f'{phi},{dist},{theta}\r\n'
        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command.encode()}")
        # self.serial.waitForBytesWritten(1000)
        

    """ Method to create a serial connection with the board
    #  @param self The object pointer"""

    @pyqtSlot(bool)
    def on_toggled(self, checked):
        self.textedit_output.append(f"{'Connected' if checked else 'Disconnected'}")
        
        self.button_connect.setText("Disconnect" if checked else "Connect")
        self.button_connect.setStyleSheet(
            "background-color: green" if checked else "background-color: red"
        )
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button_connect.setChecked(False)
        else:
            self.serial.close()


import sys
from PyQt5.QtWidgets import QApplication
from theme import ApplicationTheme


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(ApplicationTheme())
    w = RealTimeSender()

    """ 
    Initialise the Sliders 
    """

    w.show()
    sys.exit(app.exec_())
