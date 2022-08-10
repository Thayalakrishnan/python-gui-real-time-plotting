"""
LivePlotSimulator
This package contains the LivePlotSimulator class used for simulating and testing the serial connection
"""
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
AXIS_MIN = -20
AXIS_MAX = 20

X_AXIS_MIN = AXIS_MIN
X_AXIS_MAX = AXIS_MAX
Y_AXIS_MIN = AXIS_MIN
Y_AXIS_MAX = AXIS_MAX
Z_AXIS_MIN = AXIS_MIN
Z_AXIS_MAX = AXIS_MAX

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

        self.button_send_scatter_data = QPushButton(text="Send Scatter Plot", clicked=self.send_scatter_data)
        self.button_send_scatter_data.setFixedSize(120, 50)

        self.button_send_spiral_data = QPushButton(text="Send Demo Plot", clicked=self.send_demo_plot)
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
            command = f"{self.get_random_value()},{self.get_random_value()},{self.get_random_value()}\r\n"
            self.serial.write(command.encode())
            self.textedit_output.append(f"[Sent] {command}")
            #sleep(0.1)

    @pyqtSlot()
    def send_demo_plot(self):
        # create sphere parameters        
        r = 20
        pi = np.pi
        cos = np.cos
        sin = np.sin
        phi, theta = np.mgrid[0:pi:51j, 0:2 * pi:51j]
        
        x = r*sin(phi)*cos(theta)
        y = r*sin(phi)*sin(theta)
        z = r*cos(phi)
        # loop over arrays to send sphere ass cartesian coords to plot
        for i in range(len(x)):
            for j in range(len(x)):
                xdata = int(x[i][j])
                ydata = int(y[i][j])
                zdata = int(z[i][j])
                
                command = f"{xdata},{ydata},{zdata}\r\n"
                self.serial.write(command.encode())
                self.textedit_output.append(f"[Sent] {command}")
            

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
    
    def get_random_value(self):
        return self.rng.integers(low=AXIS_MIN, high=AXIS_MAX)
    
    def oldsend(self):
        # command = f'[Sent] {self.lineedit_message.text()}\r'
        x_point = self.get_random_value()
        y_point = self.get_random_value()
        z_point = self.get_random_value()
        
        command = f"{x_point},{y_point},{z_point}\r\n"

        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command.encode()}")