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


from realtimeplotter.plotter import Plotter
from realtimeplotter.detailed_graph_widget import DetailedGraphWidget
from realtimeplotter.custom_scan_widget import CustomScanWidget


""" RangeFinder Class
    This class creates an instance of the rangefiner application, inclduing the layout,
    the serial connection and the plotting options. 
    Buttons on the interface allow for interaction with the board
    
    This Class subclasses the QtWidgets to create an instance
    
    Methods from this class control the user interaction.
"""


class RealTimePlotterWidget(QtWidgets.QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(RealTimePlotterWidget, self).__init__(parent)
        self.message_le = QtWidgets.QLineEdit()
        self.message_le.setFixedSize(120, 50)
        self.send_btn = QtWidgets.QPushButton(text="Send to Board", clicked=self.send)
        self.send_btn.setFixedSize(120, 50)
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.output_te.setFixedWidth(500)
        self.button = QtWidgets.QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button.setStyleSheet("background-color: red")
        self.button.setFixedSize(120, 50)
        """ Timers (ms) """
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)
        """ Graphing """
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        self.container.setMinimumSize(QSize(500, 500))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.modifier = Plotter(graph)

        """ Buttons """
        self.button_quick_scan = QtWidgets.QPushButton()
        self.button_quick_scan.setFixedSize(120, 50)
        self.button_quick_scan.setText("Quick Scan")
        self.button_quick_scan.setStyleSheet(QSSLEDGBOX)
        self.button_deep_scan = QtWidgets.QPushButton()
        self.button_deep_scan.setFixedSize(120, 50)
        self.button_deep_scan.setText("Deep Scan")
        self.button_custom_scan = QtWidgets.QPushButton()
        self.button_custom_scan.setFixedSize(120, 50)
        self.button_custom_scan.setText("Custom Scan")
        self.button_calibrate = QtWidgets.QPushButton()
        self.button_calibrate.setFixedSize(120, 50)
        self.button_calibrate.setText("Calibrate")
        self.button_ptu_control = QtWidgets.QPushButton()
        self.button_ptu_control.setFixedSize(120, 50)
        self.button_ptu_control.setText("PTU Control")
        self.button_help = QtWidgets.QPushButton()
        self.button_help.setFixedSize(120, 50)
        self.button_help.setText("Help!?")
        """ Layout """
        horizontal_layout = QtWidgets.QHBoxLayout(self)
        vertical_layout_one = QtWidgets.QVBoxLayout()
        vertical_layout_one.addWidget(self.container, 1)
        vertical_layout_two = QtWidgets.QVBoxLayout()
        vertical_layout_two.addWidget(self.output_te)
        vertical_layout_three = QtWidgets.QVBoxLayout()
        vertical_layout_three.addWidget(self.message_le)
        vertical_layout_three.addWidget(self.send_btn)
        vertical_layout_three.addWidget(self.button)
        vertical_layout_three.addWidget(self.button_quick_scan)
        vertical_layout_three.addWidget(self.button_deep_scan)
        vertical_layout_three.addWidget(self.button_custom_scan)
        vertical_layout_three.addWidget(self.button_calibrate)
        vertical_layout_three.addWidget(self.button_ptu_control)
        vertical_layout_three.addWidget(self.button_help)

        horizontal_layout.addLayout(vertical_layout_one)
        horizontal_layout.addLayout(vertical_layout_two)
        horizontal_layout.addLayout(vertical_layout_three)
        """ Serial Connection configuration """
        self.serial = QtSerialPort.QSerialPort(
            "COM4", baudRate=QtSerialPort.QSerialPort.Baud9600, readyRead=self.receive
        )
        self.setWindowTitle("Range Finder")
        """ commands """
        self.command_quick_scan = "-on-q"
        self.command_deep_scan = "-on-l"
        self.command_custom_scan = "-c"
        self.command_ptu_control = "-test"
        self.command_calibrate = "-cal"
        self.command_help = "-help"
        self.command_d = "d"
        self.command_h = "h"

        self.plotbank = []

    """ Method to read from serial, convert the data and send it to be plotted  """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            self.output_te.append(raw_input_data)
            raw_input_data = list(map(int, raw_input_data.rstrip("\r\n").split(",")))
            theta = math.radians(raw_input_data[1])
            phi = math.radians(raw_input_data[0])
            distance = raw_input_data[2]

            x_val = distance * math.sin(theta) * math.cos(phi)
            y_val = distance * math.sin(theta) * math.sin(phi)
            z_val = distance * math.cos(theta)
            self.output_te.append(f"x = {x_val} y = {y_val} z = {z_val}")
            self.plotbank.append(f"x = {x_val} y = {y_val} z = {z_val}")
            pos = QVector3D(x_val, z_val, y_val)
            self.modifier.addCustomItem(pos)

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())

    """ Method to create a serial connection with the board
    #  @param self The object pointer"""

    @pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        self.button.setStyleSheet(
            "background-color: green" if checked else "background-color: red"
        )
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button.setChecked(False)
        else:
            self.serial.close()

    """ Quick Scan """
    """ Button to trigger a quick scan
    #  @param self The object pointer"""

    def button_quick_scan_click(self):
        self.quick_scan = DetailedGraphWidget()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_quick_scan.encode())

    """ Deep Scan """
    """ Button to trigger a deep scan
    #  @param self The object pointer"""

    def button_deep_scan_click(self):
        self.deep_scan = DetailedGraphWidget()
        self.deep_scan.show()
        self.deep_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_deep_scan.encode())

    """ Custom Scan """
    """ Button to trigger a custom scan
    #  @param self The object pointer"""

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
        self.custom_scan.button_main_menu.clicked.connect(
            self.custom_scan.button_main_menu_click
        )
        self.custom_scan.button_finish_setting_values.clicked.connect(
            self.custom_scan.button_finish_setting_values_click
        )
        self.custom_scan.show()
        self.custom_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_custom_scan.encode())

    """ Calibrate """
    """ Button to trigger a calibration
    #  @param self The object pointer"""

    def button_calibrate_click(self):
        self.quick_scan = DetailedGraphWidget()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_calibrate.encode())

    """ PTU Control """
    """ Button to control the PTU
    #  @param self The object pointer"""

    def button_ptu_control_click(self):
        self.serial.write(self.command_h.encode())

    """ Help?! """
    """ Button to trigger the help commands
    #  @param self The object pointer"""

    def button_help_click(self):
        self.serial.write(self.command_d.encode())


"""
QSSLEDGBOX =

QLabel {
    background-color: black;
    border-radius: 2px;
    padding: 10px;
    color: red;
}


self.GBox_Led.setStyleSheet(QSSLEDGBOX)
"""

QSSLEDGBOX = """
QLabel {
    background-color: black;
    border-radius: 2px;
    padding: 10px;
    color: red;
}

QLCDNumber {
    background-color: none;
    color: red;
    font-szie: 36px;    
    border: none;  
}
"""


from PyQt5.QtGui import QColor, QPalette

""" Provides the Dark Theme """


def ScatterPlotTheme():
    theme = Q3DTheme()
    theme.setAmbientLightStrength(0.3)
    theme.setBackgroundColor(QColor(QRgb(0x99CA53)))
    theme.setBackgroundEnabled(True)
    theme.setBaseColor(QColor(QRgb(0x209FDF)))
    theme.setColorStyle(Q3DTheme.ColorStyleUniform)
    theme.setFont(QFont("Impact"), 35)
    theme.setGridEnabled(True)
    theme.setGridLineColor(QColor(QRgb(0x99CA53)))
    theme.setHighlightLightStrength(7.0)
    theme.setLabelBackgroundColor(QColor(0xF6, 0xA6, 0x25, 0xA0))
    theme.setLabelBackgroundEnabled(True)
    theme.setLabelBorderEnabled(True)
    theme.setLabelTextColor(QColor(QRgb(0x404044)))
    theme.setLightColor(QColor(QColorConstants.White))
    theme.setLightStrength(6.0)
    theme.setMultiHighlightColor(QColor(QRgb(0x6D5FD5)))
    theme.setSingleHighlightColor(QColor(QRgb(0xF6A625)))
    theme.setWindowColor(QColor(QRgb(0xFFFFFF)))

    # app.setPalette(darkPalette)
    return theme
