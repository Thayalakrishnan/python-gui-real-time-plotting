"""
RealTimeSender
This package contains the RealTimeSender class used for simulating and testing the serial connection
"""
import sys
import numpy as np
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSlot, QTimer, QIODevice
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from helpers import GenericLayoutHelper
from theme import ApplicationTheme


""" RangeFinder Class
    This class creates an instance of the rangefiner application, inclduing the layout,
    the serial connection and the plotting options. 
    Buttons on the interface allow for interaction with the board
    
    This Class subclasses the QtWidgets to create an instance
    
    Methods from this class control the user interaction.
"""


class RealTimeSender(QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(RealTimeSender, self).__init__(parent)

        """
        Text and Line Edits
        """
        self.lineedit_message = QLineEdit()
        self.lineedit_message.setFixedSize(120, 50)

        self.textedit_output = QTextEdit(readOnly=True)
        self.textedit_output.setFixedWidth(500)

        """ Timers (ms) """
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """ Buttons """
        self.button_send = QPushButton(text="Send to Board", clicked=self.send)
        self.button_send.setFixedSize(120, 50)

        self.button_connect = QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button_connect.setStyleSheet("background-color: red")
        self.button_connect.setFixedSize(120, 50)

        """ Layout """
        VBox = QVBoxLayout(self)

        vbox_layout_one = QVBoxLayout()
        vbox_layout_one = GenericLayoutHelper(
            QVBoxLayout(),
            [
                self.lineedit_message,
                self.button_send,
                self.button_connect,
            ],
        )

        hbox_layout_one = QHBoxLayout()
        hbox_layout_one.addLayout(vbox_layout_one)

        hbox_layout_two = QHBoxLayout()
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

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        # command = f'[Sent] {self.lineedit_message.text()}\r'
        x_point = self.rng.integers(low=-1500, high=1500)
        y_point = self.rng.integers(low=-1500, high=1500)
        z_point = self.rng.integers(low=0, high=3000)
        command = f"{x_point},{y_point},{z_point}\r\n"

        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command.encode()}")

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
