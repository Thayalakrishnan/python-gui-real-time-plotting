"""
LivePlotSimulator
This package contains the LivePlotSimulator class used for simulating and testing the serial connection
"""
from time import sleep
import numpy as np
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSlot, QTimer, QIODevice, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


COM_PORT = "COM6"


""" RangeFinder Class
    This class creates an instance of the rangefiner application, inclduing the layout,
    the serial connection and the plotting options. 
    Buttons on the interface allow for interaction with the board
    
    This Class subclasses the QtWidgets to create an instance
    
    Methods from this class control the user interaction.
"""

def GenericLayoutHelper(layout_box, arr_widgets):
    for w in arr_widgets:
        layout_box.addWidget(w)
    return layout_box



class LivePlotSimulator(QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(LivePlotSimulator, self).__init__(parent)


        """
        Text and Line Edits
        """
        self.lineedit_message = QLineEdit()
        self.lineedit_message.setFixedSize(120, 50)

        self.textedit_output = QTextEdit(readOnly=True)
        self.textedit_output.setMinimumWidth(200)

        """ Timers (ms) """
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """ Buttons """
        self.button_send = QPushButton(text="Send Custom Data", clicked=self.send)
        self.button_send.setFixedSize(120, 50)

        self.button_send_scatter_data = QPushButton(text="Send Scatter Data", clicked=self.send_scatter_data)
        self.button_send_scatter_data.setFixedSize(120, 50)

        self.button_send_spiral_data = QPushButton(text="Send Scatter Data", clicked=self.send_spiral_data)
        self.button_send_spiral_data.setFixedSize(120, 50)

        self.button_connect = QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button_connect.setStyleSheet("background-color: red")
        self.button_connect.setFixedSize(120, 50)

        """ Layout """
        HBox = QHBoxLayout(self)

        vbox_buttons = QVBoxLayout()
        vbox_buttons.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        vbox_buttons.addWidget(self.lineedit_message,)
        vbox_buttons.addWidget(self.button_send,)
        vbox_buttons.addWidget(self.button_connect,)
        vbox_buttons.addWidget(self.button_send_scatter_data,)
        vbox_buttons.addWidget(self.button_send_spiral_data,)


        vbox_textedit = QVBoxLayout()
        vbox_textedit.addWidget(self.textedit_output, 1)

        HBox.addLayout(vbox_textedit)
        HBox.addLayout(vbox_buttons)

        self.setWindowTitle("Live Plot Simulator")

        """ commands """
        self.command_d = "d"
        self.command_h = "h"

        self.plotbank = []

        """ Serial Connection configuration """
        self.serial = QtSerialPort.QSerialPort(
            COM_PORT,
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

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        command = f"{self.lineedit_message.text()}\r\n"
        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command}")

    @pyqtSlot()
    def send_scatter_data(self):
        
        for i in range(100):
            command = f"{self.get_x_value()},{self.get_y_value()},{self.get_z_value()}\r\n"
            self.serial.write(command.encode())
            self.textedit_output.append(f"[Sent] {command}")
            #sleep(0.1)

    @pyqtSlot()
    def send_spiral_data(self):
        for i in range(100):
            zdata = self.get_z_value()
            xdata = int(np.sin(zdata) + self.rng.integers(low=0, high=1000))
            ydata = int(np.cos(zdata) + self.rng.integers(low=0, high=1000))
            
            command = f"{xdata},{ydata},{zdata}\r\n"
            self.serial.write(command.encode())
            self.textedit_output.append(f"[Sent] {command}")
            #sleep(0.1)

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
                if not self.serial.open(QIODevice.ReadWrite):
                    self.button_connect.setChecked(False)
        else:
            self.serial.close()
    
    def get_x_value(self):
        return self.rng.integers(low=0, high=1000)
    
    def get_y_value(self):
        return self.rng.integers(low=0, high=1000)
    
    def get_z_value(self):
        return self.rng.integers(low=0, high=1000)
    
    
    def oldsend(self):
        # command = f'[Sent] {self.lineedit_message.text()}\r'
        x_point = self.rng.integers(low=0, high=1000)
        y_point = self.rng.integers(low=0, high=1000)
        z_point = self.rng.integers(low=0, high=1000)
        
        command = f"{x_point},{y_point},{z_point}\r\n"

        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command.encode()}")