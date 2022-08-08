import collections, math, struct, sys, time, copy, serial
import numpy as np
from threading import Thread
from PyQt5 import QtSerialPort
from qtpy.uic import loadUi
#from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QLocale, QObject, QSize, Qt, QTimer, pyqtSignal, pyqtSlot
from qtpy.QtGui import QColor, QColorConstants, QFont, QVector3D, qRgb, QPalette
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, 
                            QFontComboBox, QFrame, QHBoxLayout, QLabel, 
                            QLCDNumber, QMainWindow, QPushButton, 
                            QSizePolicy, QSlider, QVBoxLayout, QWidget, QStyleFactory, QStyle)
from qtpy.QtDatavisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
                                      QAbstract3DAxis, QAbstract3DGraph,
                                      QAbstract3DSeries, QCustom3DItem,
                                      QScatter3DSeries, QScatterDataItem,
                                      QScatterDataProxy, QValue3DAxis,
                                      QValue3DAxisFormatter)

class RangeFinder(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RangeFinder, self).__init__(parent)
        self.message_le = QtWidgets.QLineEdit()
        self.message_le.setFixedSize(120,50)
        self.send_btn = QtWidgets.QPushButton(text="Send to Board",clicked=self.send)
        self.send_btn.setFixedSize(120,50)
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.output_te.setFixedWidth(500)
        self.button = QtWidgets.QPushButton(text="Connect", checkable=True,toggled=self.on_toggled)
        self.button.setStyleSheet("background-color: red")
        self.button.setFixedSize(120,50)
        ''' Timers (ms) '''
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)
        ''' Graphing '''
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        self.container.setMinimumSize(QSize(500, 500))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.modifier = RangeFinderPlotter(graph)
        ''' Buttons '''
        self.button_quick_scan = QtWidgets.QPushButton()
        self.button_quick_scan.setFixedSize(120,50)
        self.button_quick_scan.setText("Quick Scan")
        self.button_deep_scan = QtWidgets.QPushButton()
        self.button_deep_scan.setFixedSize(120,50)
        self.button_deep_scan.setText("Deep Scan")
        self.button_custom_scan = QtWidgets.QPushButton()
        self.button_custom_scan.setFixedSize(120,50)
        self.button_custom_scan.setText("Custom Scan")
        self.button_calibrate = QtWidgets.QPushButton()
        self.button_calibrate.setFixedSize(120,50)
        self.button_calibrate.setText("Calibrate")
        self.button_ptu_control = QtWidgets.QPushButton()
        self.button_ptu_control.setFixedSize(120,50)
        self.button_ptu_control.setText("PTU Control")
        self.button_help = QtWidgets.QPushButton()
        self.button_help.setFixedSize(120,50)
        self.button_help.setText("Help!?")
        ''' Layout '''
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
        self.serial = QtSerialPort.QSerialPort('COM4',baudRate=QtSerialPort.QSerialPort.Baud9600,readyRead=self.receive)
        self.setWindowTitle("Range Finder")
        ''' commands '''
        self.command_quick_scan = '-on-q'
        self.command_deep_scan = '-on-l'
        self.command_custom_scan = '-c'
        self.command_ptu_control= '-test'
        self.command_calibrate = '-cal'
        self.command_help = '-help'
        self.command_d = 'd'
        self.command_h = 'h'
        
        self.plotbank = []

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            self.output_te.append(raw_input_data)
            raw_input_data = list(map(int, raw_input_data.rstrip('\r\n').split(',')))
            theta = math.radians(raw_input_data[1])
            phi = math.radians(raw_input_data[0])
            distance = raw_input_data[2]

            x_val = distance*math.sin(theta)*math.cos(phi)
            y_val = distance*math.sin(theta)*math.sin(phi)
            z_val = distance*math.cos(theta)
            self.output_te.append(f'x = {x_val} y = {y_val} z = {z_val}')
            self.plotbank.append(f'x = {x_val} y = {y_val} z = {z_val}')
            pos = QVector3D(x_val,z_val,y_val)
            self.modifier.addCustomItem(pos)
    
    @QtCore.pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())
    
    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        self.button.setStyleSheet("background-color: green" if checked else "background-color: red")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button.setChecked(False)
        else:
            self.serial.close()
            
    
    ''' Quick Scan '''
    def button_quick_scan_click(self):
        self.quick_scan = GraphConsole()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_quick_scan.encode())
    ''' Deep Scan '''
    def button_deep_scan_click(self):
        self.deep_scan = GraphConsole()
        self.deep_scan.show()
        self.deep_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_deep_scan.encode())
    ''' Custom Scan '''
    def button_custom_scan_click(self):
        self.custom_scan = CustomScanConsole()
        ''' Sliders '''
        self.custom_scan.slider_azimuth_max.valueChanged.connect(self.custom_scan.azimuth_max_change)
        self.custom_scan.slider_azimuth_min.valueChanged.connect(self.custom_scan.azimuth_min_change)
        self.custom_scan.slider_elevation_max.valueChanged.connect(self.custom_scan.elevation_max_change)
        self.custom_scan.slider_elevation_min.valueChanged.connect(self.custom_scan.elevation_min_change)
        self.custom_scan.slider_scan_frequency.valueChanged.connect(self.custom_scan.scan_frequency_change)
        self.custom_scan.slider_step_change.valueChanged.connect(self.custom_scan.step_change_change)
        self.custom_scan.slider_samples_orientation.valueChanged.connect(self.custom_scan.samples_orientation_change)
        ''' Buttons '''
        self.custom_scan.button_main_menu.clicked.connect(self.custom_scan.button_main_menu_click)
        self.custom_scan.button_finish_setting_values.clicked.connect(self.custom_scan.button_finish_setting_values_click)
        self.custom_scan.show()
        self.custom_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_custom_scan.encode())
    ''' Calibrate '''
    def button_calibrate_click(self):
        self.quick_scan = GraphConsole()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_calibrate.encode())
    ''' PTU Control '''
    def button_ptu_control_click(self):
        #worself.quick_scan = GraphConsole()
        #self.quick_scan.show()
        #self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_h.encode())
    ''' Help?! '''
    def button_help_click(self):
        #self.quick_scan = GraphConsole()
        #self.quick_scan.show()
        #self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_d.encode())

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = RangeFinder()
    
    ''' Sliders '''
    w.button_quick_scan.clicked.connect(w.button_quick_scan_click)
    w.button_deep_scan.clicked.connect(w.button_deep_scan_click)
    w.button_custom_scan.clicked.connect(w.button_custom_scan_click)
    w.button_calibrate.clicked.connect(w.button_calibrate_click)
    w.button_ptu_control.clicked.connect(w.button_ptu_control_click)
    w.button_help.clicked.connect(w.button_help_click)
    DarkTheme(app)
    w.show()
    sys.exit(app.exec_())
    
    

''' 
import collections
import copy
import math
import struct
import sys
import time
from threading import Thread
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import serial
from PyQt5 import QtCore, QtGui, QtSerialPort, QtWidgets
from PyQt5.QtCore import (QLocale, QObject, QSize, Qt, QTimer, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtGui import QColor, QColorConstants, QFont, QVector3D, qRgb, QPalette
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFontComboBox, QFrame,
    QHBoxLayout, QLabel, QLCDNumber, QMainWindow, QPushButton, QSizePolicy,
    QSlider, QVBoxLayout, QWidget)
from PyQt5.uic import loadUi
from qtpy.QtDatavisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
                                      QAbstract3DAxis, QAbstract3DGraph,
                                      QAbstract3DSeries, QCustom3DItem,
                                      QScatter3DSeries, QScatterDataItem,
                                      QScatterDataProxy, QValue3DAxis,
                                      QValue3DAxisFormatter)

from qtpy.QtCore import QStateMachine, QPropertyAnimation, QEventTransition, QState, QEasingCurve, QEvent

from qtpy.QtCore import QObject, QSize, Qt, QLocale
from qtpy.QtGui import QFont, QVector3D, QColor, QColorConstants, QPalette
from qtpy.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QStyleFactory, QStyle
'''
