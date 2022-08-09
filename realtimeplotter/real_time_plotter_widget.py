""" @package RangeFinder
  This package contains all the classes that are used to create an instance of the GUI
  The classes dont take any input and run off of each other. Button input triggers the 
 instance of one of these classes as every class generates a new window, except the plotting 
"""
from PyQt5 import QtSerialPort
from PyQt5.QtCore import (
    pyqtSlot, 
    QSize, 
    Qt, 
    QTimer, 
    QIODevice
)
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy
)
from PyQt5.QtDataVisualization import (
    Q3DScatter
)
from PyQt5.QtGui import (
    QVector3D
)
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
        #self.textedit_output.setFixedWidth(500)        
        
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
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.graph_container = QWidget.createWindowContainer(graph)
        self.graph_container.setMinimumSize(QSize(500, 500))
        self.graph_container.setMaximumSize(screenSize)
        self.graph_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_container.setFocusPolicy(Qt.StrongFocus)
        self.graph_modifed = Plotter(graph)

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
        
        """
        Layout 
        """
        VBox = QVBoxLayout(self)
        
        vbox_layout_one = QVBoxLayout()
        vbox_layout_one = GenericLayoutHelper(
            QVBoxLayout(), 
            [
                self.lineedit_message,
                self.button_send,
                self.button_connect,
                self.button_quick_scan,
                self.button_deep_scan,
                self.button_custom_scan,
                self.button_calibrate,
                self.button_ptu_control,
                self.button_help
            ]
        )
        
        hbox_layout_one = QHBoxLayout()
        hbox_layout_one.addWidget(self.graph_container)
        hbox_layout_one.addLayout(vbox_layout_one)
        
        hbox_layout_two = QHBoxLayout()
        hbox_layout_two.addWidget(self.textedit_output, 1)
        
        VBox.addLayout(hbox_layout_one)
        VBox.addLayout(hbox_layout_two)
        
        """
        Serial Connection configuration 
        """
        self.serial = QtSerialPort.QSerialPort(
            "COM5", 
            baudRate=QtSerialPort.QSerialPort.Baud9600, 
            readyRead=self.receive
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

    """
    Method to read from serial, convert the data and send it to be plotted  
    """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            raw_input_data = list(map(int, raw_input_data.rstrip("\r\n").split(",")))
            #phi = math.radians(raw_input_data[0])
            #theta = math.radians(raw_input_data[1])
            #distance = raw_input_data[2]
            #x_val = distance * math.sin(theta) * math.cos(phi)
            #y_val = distance * math.sin(theta) * math.sin(phi)
            #z_val = distance * math.cos(theta)
            x_val = raw_input_data[0]
            y_val = raw_input_data[1]
            z_val = raw_input_data[2]
            self.textedit_output.append(f"x = {x_val} y = {y_val} z = {z_val}")
            self.plotbank.append(f"x = {x_val} y = {y_val} z = {z_val}")
            pos = QVector3D(x_val, z_val, y_val)
            self.graph_modifed.addCustomItem(pos)

    """
    Method to send commands via serial
    #  @param self The object pointer
    # """

    @pyqtSlot()
    def send(self):
        #self.serial.write(self.lineedit_message.text().encode())
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