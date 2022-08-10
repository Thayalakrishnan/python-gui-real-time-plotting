"""
RealTimePlotterWidget
"""
import math
from turtle import width

from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSlot, QSize, Qt, QTimer, QIODevice
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from PyQt5.QtDataVisualization import Q3DScatter
from PyQt5.QtGui import QVector3D

from realtimeplotter.plotter import Plotter
from realtimeplotter.detailed_graph_widget import DetailedGraphWidget
from realtimeplotter.custom_scan_widget import CustomScanWidget
from realtimeplotter.helpers import GenericLayoutHelper

""" 
RangeFinder Class
This class creates an instance of the rangefiner application, inclduing the layout,
the serial connection and the plotting options. 
Buttons on the interface allow for interaction with the board

This Class subclasses the QtWidgets to create an instance

Methods from this class control the user interaction.
"""


COM_PORT = "COM5"

class RealTimePlotterWidget(QWidget):
    """
    The constructor.
    """

    def __init__(self, parent=None):
        super(RealTimePlotterWidget, self).__init__(parent)
        """
        Text and Line Edits
        """
        self.lineedit_message = QLineEdit()
        self.lineedit_message.setFixedSize(120, 50)

        self.textedit_output = QTextEdit(readOnly=True)
        # self.textedit_output.setFixedWidth(500)

        """
        Timers (ms) 
        """
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """
        Graphing 
        """
        self.graph_instance = Plotter()
        self.graph_container = self.graph_instance.graph_container

        """
        Buttons 
        """
        self.button_send = QPushButton(text="Send to Board", clicked=self.send)
        self.button_send.setFixedSize(120, 50)

        self.button_connect = QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button_connect.setStyleSheet("background-color: red")
        self.button_connect.setFixedSize(120, 50)

        self.button_quick_scan = QPushButton()
        self.button_quick_scan.setFixedSize(120, 50)
        self.button_quick_scan.setText("Quick Scan")

        self.button_deep_scan = QPushButton()
        self.button_deep_scan.setFixedSize(120, 50)
        self.button_deep_scan.setText("Deep Scan")

        self.button_custom_scan = QPushButton()
        self.button_custom_scan.setFixedSize(120, 50)
        self.button_custom_scan.setText("Custom Scan")

        self.button_calibrate = QPushButton()
        self.button_calibrate.setFixedSize(120, 50)
        self.button_calibrate.setText("Calibrate")

        self.button_ptu_control = QPushButton()
        self.button_ptu_control.setFixedSize(120, 50)
        self.button_ptu_control.setText("PTU Control")

        self.button_help = QPushButton()
        self.button_help.setFixedSize(120, 50)
        self.button_help.setText("Help!?")

        self.button_reset_plot = QPushButton(
            self,
            text="Reset Plot", 
            clicked=self.button_reset_plot_click
        )
        self.button_reset_plot.setFixedSize(120, 50)
        #self.button_reset_plot.setText("Reset Plot")
        
        
        """
        Layout 
        """
        hbox = QHBoxLayout(self)

        vbox_buttons = QVBoxLayout()
        vbox_buttons.addWidget(self.lineedit_message)
        vbox_buttons.addWidget(self.button_send)
        vbox_buttons.addWidget(self.button_connect)
        vbox_buttons.addWidget(self.button_quick_scan)
        vbox_buttons.addWidget(self.button_deep_scan)
        vbox_buttons.addWidget(self.button_custom_scan)
        vbox_buttons.addWidget(self.button_calibrate)
        vbox_buttons.addWidget(self.button_ptu_control)
        vbox_buttons.addWidget(self.button_help)
        vbox_buttons.addWidget(self.button_reset_plot)
        vbox_buttons.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        vbox_texedit = QVBoxLayout()
        vbox_texedit.addWidget(self.textedit_output)

        hbox.addWidget(self.graph_container)
        hbox.addLayout(vbox_texedit)
        hbox.addLayout(vbox_buttons)
        

        """
        Serial Connection configuration 
        """
        self.serial = QtSerialPort.QSerialPort(
            COM_PORT, baudRate=QtSerialPort.QSerialPort.Baud9600, readyRead=self.receive
        )

        self.serial.open(self.serial.ReadWrite)
        self.setWindowTitle("Range Finder")

        """
        commands 
        """
        self.command_quick_scan = "-on-q"
        self.command_deep_scan = "-on-l"
        self.command_custom_scan = "-c"
        self.command_ptu_control = "-test"
        self.command_calibrate = "-cal"
        self.command_help = "-help"
        self.command_d = "d"
        self.command_h = "h"

        self.plotbank = []
        self.counter = 0

    """
    Method to read from serial, convert the data and send it to be plotted  
    """
    #  @param self The object pointer
    
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            x_val, y_val, z_val = map(int, raw_input_data.rstrip("\r\n").split(","))
            #self.textedit_output.append(f"({x_val}, {y_val}, {z_val})")
            
            self.counter += 1
            self.textedit_output.append(f"{self.counter}")
            
            pos = QVector3D(x_val, z_val, y_val)
            self.graph_instance.add_new_item(pos)
            

    @pyqtSlot()
    def receive_production(self):
        while self.serial.canReadLine():
            # get the data
            raw_input_data = self.serial.readLine().data().decode()
            raw_input_data = list(map(int, raw_input_data.rstrip("\r\n").split(",")))
            
            # convert the data to be plotted on  a cartesian plot in 3D
            phi = math.radians(raw_input_data[0])
            theta = math.radians(raw_input_data[1])
            distance = raw_input_data[2]
            
            x_val = distance * math.sin(theta) * math.cos(phi)
            y_val = distance * math.sin(theta) * math.sin(phi)
            z_val = distance * math.cos(theta)
            
            self.plotbank.append((x_val, z_val, y_val))
            self.textedit_output.append(f"({x_val}, {y_val}, {z_val})")
            
            # send the point to be plotted
            pos = QVector3D(x_val, z_val, y_val)
            self.graph_instance.add_new_item(pos)

    """
    Method to send commands via serial
    #  @param self The object pointer
    # """

    @pyqtSlot()
    def send(self):
        # self.serial.write(self.lineedit_message.text().encode())
        command = f'{"hello"}\r\n'
        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command}")
        # self.serial.waitForBytesWritten(1000)

    """ 
    # Method to create a serial connection with the board
    # @param self The object pointer
    # """

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

    """ 
    # Quick Scan 
    # Button to trigger a quick scan
    # @param self The object pointer
    # """

    def button_quick_scan_click(self):
        self.quick_scan = DetailedGraphWidget()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_quick_scan.encode())

    """ 
    # Deep Scan
    # Button to trigger a deep scan
    # @param self The object pointer
    # """

    def button_deep_scan_click(self):
        self.deep_scan = DetailedGraphWidget()
        self.deep_scan.show()
        self.deep_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_deep_scan.encode())

    """ 
    # Custom Scan 
    # Button to trigger a custom scan
    # @param self The object pointer
    # """

    def button_custom_scan_click(self):
        self.custom_scan = CustomScanWidget()

        self.custom_scan.slider_azimuth_max.valueChanged.connect(
            self.custom_scan.azimuth_max_change
        )
        self.custom_scan.slider_azimuth_min.valueChanged.connect(
            self.custom_scan.azimuth_min_change
        )
        self.custom_scan.slider_elevation_max.valueChanged.connect(
            self.custom_scan.elevation_max_change
        )
        self.custom_scan.slider_elevation_min.valueChanged.connect(
            self.custom_scan.elevation_min_change
        )
        self.custom_scan.slider_scan_frequency.valueChanged.connect(
            self.custom_scan.scan_frequency_change
        )
        self.custom_scan.slider_step_change.valueChanged.connect(
            self.custom_scan.step_change_change
        )
        self.custom_scan.slider_samples_orientation.valueChanged.connect(
            self.custom_scan.samples_orientation_change
        )
        self.custom_scan.button_close.clicked.connect(
            self.custom_scan.button_close_click
        )
        self.custom_scan.button_proceed.clicked.connect(
            self.custom_scan.button_proceed_click
        )

        self.custom_scan.show()
        self.custom_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_custom_scan.encode())

    """ 
    # Calibrate
    # Button to trigger a calibration
    # @param self The object pointer
    # """

    def button_calibrate_click(self):
        self.quick_scan = DetailedGraphWidget()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_calibrate.encode())

    """ 
    # PTU Control
    # Button to control the PTU
    # @param self The object pointer
    # """

    def button_ptu_control_click(self):
        self.serial.write(self.command_h.encode())

    """ 
    # Help?!
    # Button to trigger the help commands
    # @param self The object pointer
    # """

    def button_help_click(self):
        self.serial.write(self.command_d.encode())

    def button_reset_plot_click(self):
        print("Reset!")
