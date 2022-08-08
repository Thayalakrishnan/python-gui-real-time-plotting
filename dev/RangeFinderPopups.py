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
from PyQt5.QtWidgets import QStyleFactory, QStyle
import qdarkstyle
import math
import sys
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from qtpy.QtDatavisualization import Q3DScatter
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtDatavisualization import QValue3DAxis
from qtpy.QtWidgets import  QMainWindow, QPushButton, QLCDNumber, QSlider, QFrame
from qtpy.uic import loadUi
from qtpy.QtCore import QObject, QSize, Qt, QLocale
from qtpy.QtGui import QFont, QVector3D, QColor, QColorConstants, QPalette
from qtpy.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget



from RangeFinderPlotter import RangeFinderPlotter
from RangeFinderSupport import DarkTheme

class ScanChooser(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ScanChooser, self).__init__(parent)
        self.message_le = QtWidgets.QLineEdit()
        self.send_btn = QtWidgets.QPushButton(text="Send",clicked=self.send)
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.button = QtWidgets.QPushButton(text="Connect", checkable=True,toggled=self.on_toggled)
        
        #self.graph = pg.GraphicsWindow()
        ''' Embedding the graph'''
        # horizontal layout
        graph = Q3DScatter()
        # container
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.container.sizePolicy().hasHeightForWidth())
        self.container.setSizePolicy(sizePolicy)
        self.container.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.container.setObjectName("self.container")
        
        self.modifier = RangeFinderPlotter(graph)
        
        
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.message_le)
        hlay.addWidget(self.send_btn)
        hlay.addWidget(self.container)
        lay.addLayout(hlay)
        lay.addWidget(self.output_te)
        lay.addWidget(self.button)



class Popup(QWidget):
    def __init__(self):
        super().__init__()

class PopupP(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PopupP, self).__init__(parent)


''' Generate the Graphing Console '''
class GraphConsole(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GraphConsole, self).__init__(parent)
        ''' Widgets '''
        self.run_scan = QtWidgets.QPushButton(text="Run Scan")
        self.run_scan.setFixedSize(120,50)
        self.stop_scan = QtWidgets.QPushButton(text="Stop Scan")
        self.stop_scan.setFixedSize(120,50)
        ''' Accelerometer '''
        self.lcd_acc = QtWidgets.QLCDNumber()
        self.lcd_acc.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_acc.setSmallDecimalPoint(False)
        self.lcd_acc.setObjectName("lcd_acc")
        self.lcd_acc.setFixedSize(120,50)
        ''' Gyroscope '''
        self.lcd_gyr = QtWidgets.QLCDNumber()
        self.lcd_gyr.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_gyr.setSmallDecimalPoint(False)
        self.lcd_gyr.setObjectName("lcd_gyr")
        self.lcd_gyr.setFixedSize(120,50)
        ''' Magnetometer '''
        self.lcd_mag = QtWidgets.QLCDNumber()
        self.lcd_mag.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_mag.setSmallDecimalPoint(False)
        self.lcd_mag.setObjectName("lcd_mag")
        self.lcd_mag.setFixedSize(120,50)
        ''' Azimuth '''
        self.lcd_azi = QtWidgets.QLCDNumber()
        self.lcd_azi.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_azi.setSmallDecimalPoint(False)
        self.lcd_azi.setObjectName("lcd_azi")
        self.lcd_azi.setFixedSize(120,50)
        ''' Elevation '''
        self.lcd_ele = QtWidgets.QLCDNumber()
        self.lcd_ele.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_ele.setSmallDecimalPoint(False)
        self.lcd_ele.setObjectName("lcd_ele")
        self.lcd_ele.setFixedSize(120,50)
        ''' Distance '''
        self.lcd_dis = QtWidgets.QLCDNumber()
        self.lcd_dis.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_dis.setSmallDecimalPoint(False)
        self.lcd_dis.setObjectName("lcd_dis")
        self.lcd_dis.setFixedSize(120,50)
        
        ''' Graphing '''
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        self.container.setMinimumSize(QSize(screenSize.width() / 2, screenSize.height() / 1.5))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.modifier = RangeFinderPlotter(graph)
        
        ''' Labels '''
        self.label_acc = QtWidgets.QLabel()
        self.label_acc.setFixedSize(120,50)
        self.label_acc.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_acc.setAlignment(QtCore.Qt.AlignCenter)
        self.label_acc.setText("Accelerometer")
        
        self.label_gyr = QtWidgets.QLabel()
        self.label_gyr.setFixedSize(120,50)
        self.label_gyr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_gyr.setAlignment(QtCore.Qt.AlignCenter)
        self.label_gyr.setText("Gyroscope")
        
        self.label_mag = QtWidgets.QLabel()
        self.label_mag.setFixedSize(120,50)
        self.label_mag.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_mag.setAlignment(QtCore.Qt.AlignCenter)
        self.label_mag.setText("Magnetometer")
        
        self.label_azi = QtWidgets.QLabel()
        self.label_azi.setFixedSize(120,50)
        self.label_azi.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azi.setText("Azimuth")
        
        self.label_ele = QtWidgets.QLabel()
        self.label_ele.setFixedSize(120,50)
        self.label_ele.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_ele.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ele.setText("Elevation")
        
        self.label_dis = QtWidgets.QLabel()
        self.label_dis.setFixedSize(120,50)
        self.label_dis.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_dis.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dis.setText("Distance")
        
        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.horizontal_layout.addWidget(self.container, 1)
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addWidget(self.run_scan)
        self.vertical_layout.addWidget(self.stop_scan)
        self.vertical_layout.addWidget(self.label_acc)
        self.vertical_layout.addWidget(self.lcd_acc)
        self.vertical_layout.addWidget(self.label_gyr)
        self.vertical_layout.addWidget(self.lcd_gyr)
        self.vertical_layout.addWidget(self.label_mag)
        self.vertical_layout.addWidget(self.lcd_mag)
        self.vertical_layout.addWidget(self.label_azi)
        self.vertical_layout.addWidget(self.lcd_azi)
        self.vertical_layout.addWidget(self.label_ele)
        self.vertical_layout.addWidget(self.lcd_ele)
        self.vertical_layout.addWidget(self.label_dis)
        self.vertical_layout.addWidget(self.lcd_dis)
        self.setWindowTitle("Graph Console")


''' Generate the Graphing Console '''
class CustomScanConsole(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CustomScanConsole, self).__init__(parent)
        ''' Widgets '''
        self.button_finish_setting_values = QtWidgets.QPushButton(text="Proceed")
        self.button_finish_setting_values.setFixedSize(120,50)
        self.button_main_menu = QtWidgets.QPushButton(text="Main Menu")
        self.button_main_menu.setFixedSize(120,50)
        self.serial = QtSerialPort.QSerialPort('COM4',baudRate=QtSerialPort.QSerialPort.Baud9600)
        # configure global application font
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setKerning(False)
        
        ''' set bounds '''
        set_azimuth_min_low = 30
        set_azimuth_min_high = 155
        set_azimuth_min_step = 1
        set_azimuth_max_low = 35
        set_azimuth_max_high = 160
        set_azimuth_max_step = 1
        set_elevate_min_low = -60
        set_elevate_min_high = 55
        set_elevate_min_step = 1
        set_elevate_max_low = -55
        set_elevate_max_high = 60
        set_elevate_max_step = 1
        set_sample_frequency_low = 1
        set_sample_frequency_high = 100
        set_sample_frequency_step = 1
        set_samples_per_orientation_low = 3
        set_samples_per_orientation_high = 10
        set_samples_per_orientation_step = 1
        set_step_change_low = 5
        set_step_change_high = 200
        set_step_change_step = 1
        
        self.groupbox_custom_scan = QtWidgets.QGroupBox()
        self.groupbox_custom_scan.setFont(font)
        
        ''' Accelerometer '''
        self.lcd_acc = QtWidgets.QLCDNumber()
        self.lcd_acc.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_acc.setSmallDecimalPoint(False)
        self.lcd_acc.setObjectName("lcd_acc")
        self.lcd_acc.setFixedSize(120,50)
        
        '''begin'''
        self.label_azimuth_max = QtWidgets.QLabel()
        self.label_azimuth_max.setFixedSize(120,50)
        self.label_azimuth_max.setFont(font)
        self.label_azimuth_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azimuth_max.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azimuth_max.setText("Azimuth Max")

        self.label_azimuth_min = QtWidgets.QLabel()
        self.label_azimuth_min.setFixedSize(120,50)
        self.label_azimuth_min.setFont(font)
        self.label_azimuth_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azimuth_min.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azimuth_min.setText("Azimuth Min")
        
        self.label_elevation_max = QtWidgets.QLabel()
        self.label_elevation_max.setFixedSize(120,50)
        self.label_elevation_max.setFont(font)
        self.label_elevation_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_elevation_max.setAlignment(QtCore.Qt.AlignCenter)
        self.label_elevation_max.setText("Elevation Max")
        
        self.label_elevation_min = QtWidgets.QLabel()
        self.label_elevation_min.setFixedSize(120,50)
        self.label_elevation_min.setFont(font)
        self.label_elevation_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_elevation_min.setAlignment(QtCore.Qt.AlignCenter)
        self.label_elevation_min.setText("Elevation Max")
        
        self.label_step_change = QtWidgets.QLabel()
        self.label_step_change.setFixedSize(120,50)
        self.label_step_change.setFont(font)
        self.label_step_change.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_step_change.setAlignment(QtCore.Qt.AlignCenter)
        self.label_step_change.setText("Step Change")
        
        self.label_scan_frequency = QtWidgets.QLabel()
        self.label_scan_frequency.setFixedSize(120,50)
        self.label_scan_frequency.setFont(font)
        self.label_scan_frequency.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_scan_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.label_scan_frequency.setText("Scan Frequency")
        
        self.label_samples_orientation = QtWidgets.QLabel()
        self.label_samples_orientation.setFixedSize(120,50)
        self.label_samples_orientation.setFont(font)
        self.label_samples_orientation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_samples_orientation.setAlignment(QtCore.Qt.AlignCenter)
        self.label_samples_orientation.setText("Samples/Orientation")
        
        '''sliders start'''
        self.slider_azimuth_max = QtWidgets.QSlider()
        self.slider_azimuth_max.setFixedSize(250,50)
        self.slider_azimuth_max.setFont(font)
        self.slider_azimuth_max.setOrientation(QtCore.Qt.Horizontal)
        self.slider_azimuth_max.setMinimum(set_azimuth_min_low)
        self.slider_azimuth_max.setMaximum(set_azimuth_min_high)
        self.slider_azimuth_max.setSingleStep(set_azimuth_min_step)
        
        self.slider_azimuth_min = QtWidgets.QSlider()
        self.slider_azimuth_min.setFixedSize(250,50)
        self.slider_azimuth_min.setFont(font)
        self.slider_azimuth_min.setOrientation(QtCore.Qt.Horizontal)
        self.slider_azimuth_min.setMinimum(set_azimuth_max_low)
        self.slider_azimuth_min.setMaximum(set_azimuth_max_high)
        self.slider_azimuth_min.setSingleStep(set_azimuth_max_step)
        
        self.slider_scan_frequency = QtWidgets.QSlider()
        self.slider_scan_frequency.setFixedSize(250,50)
        self.slider_scan_frequency.setFont(font)
        self.slider_scan_frequency.setOrientation(QtCore.Qt.Horizontal)
        self.slider_scan_frequency.setMinimum(set_sample_frequency_low)
        self.slider_scan_frequency.setMaximum(set_sample_frequency_high)
        self.slider_scan_frequency.setSingleStep(set_sample_frequency_step)

        self.slider_elevation_max = QtWidgets.QSlider()
        self.slider_elevation_max.setFixedSize(250,50)
        self.slider_elevation_max.setFont(font)
        self.slider_elevation_max.setOrientation(QtCore.Qt.Horizontal)
        self.slider_elevation_max.setMinimum(set_elevate_max_low)
        self.slider_elevation_max.setMaximum(set_elevate_max_high)
        self.slider_elevation_max.setSingleStep(set_elevate_max_step)

        self.slider_elevation_min = QtWidgets.QSlider()
        self.slider_elevation_min.setFixedSize(250,50)
        self.slider_elevation_min.setFont(font)
        self.slider_elevation_min.setOrientation(QtCore.Qt.Horizontal)
        self.slider_elevation_min.setMinimum(set_elevate_min_low)
        self.slider_elevation_min.setMaximum(set_elevate_min_high)
        self.slider_elevation_min.setSingleStep(set_elevate_min_step)
        
        self.slider_step_change = QtWidgets.QSlider()
        self.slider_step_change.setFixedSize(250,50)
        self.slider_step_change.setFont(font)
        self.slider_step_change.setOrientation(QtCore.Qt.Horizontal)
        self.slider_step_change.setMinimum(set_step_change_low)
        self.slider_step_change.setMaximum(set_step_change_high)
        self.slider_step_change.setSingleStep(set_step_change_step)
        
        self.slider_samples_orientation = QtWidgets.QSlider()
        self.slider_samples_orientation.setFixedSize(250,50)
        self.slider_samples_orientation.setFont(font)
        self.slider_samples_orientation.setOrientation(QtCore.Qt.Horizontal)
        self.slider_samples_orientation.setMinimum(set_samples_per_orientation_low)
        self.slider_samples_orientation.setMaximum(set_samples_per_orientation_high)
        self.slider_samples_orientation.setSingleStep(set_samples_per_orientation_step)
        ''' sliders end '''
        
        ''' LCD '''
        self.lcd_azimuth_max = QtWidgets.QLCDNumber()
        self.lcd_azimuth_max.setFixedSize(120,50)
        self.lcd_azimuth_max.setFont(font)
        self.lcd_azimuth_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_azimuth_max.setFrameShadow(QtWidgets.QFrame.Plain)
        
        self.lcd_azimuth_min = QtWidgets.QLCDNumber()
        self.lcd_azimuth_min.setFixedSize(120,50)
        self.lcd_azimuth_min.setFont(font)
        self.lcd_azimuth_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_azimuth_min.setFrameShadow(QtWidgets.QFrame.Plain)
        
        self.lcd_elevation_max = QtWidgets.QLCDNumber()
        self.lcd_elevation_max.setFixedSize(120,50)
        self.lcd_elevation_max.setFont(font)
        self.lcd_elevation_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_elevation_max.setFrameShadow(QtWidgets.QFrame.Plain)
        
        self.lcd_elevation_min = QtWidgets.QLCDNumber()
        self.lcd_elevation_min.setFixedSize(120,50)
        self.lcd_elevation_min.setFont(font)
        self.lcd_elevation_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_elevation_min.setFrameShadow(QtWidgets.QFrame.Plain)
        
        self.lcd_step_change = QtWidgets.QLCDNumber()
        self.lcd_step_change.setFixedSize(120,50)
        self.lcd_step_change.setFont(font)
        self.lcd_step_change.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_step_change.setFrameShadow(QtWidgets.QFrame.Plain)

        self.lcd_scan_frequency = QtWidgets.QLCDNumber()
        self.lcd_scan_frequency.setFixedSize(120,50)
        self.lcd_scan_frequency.setFont(font)
        self.lcd_scan_frequency.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_scan_frequency.setFrameShadow(QtWidgets.QFrame.Plain)
        
        self.lcd_samples_orientation = QtWidgets.QLCDNumber()
        self.lcd_samples_orientation.setFixedSize(120,50)
        self.lcd_samples_orientation.setFont(font)
        self.lcd_samples_orientation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_samples_orientation.setFrameShadow(QtWidgets.QFrame.Plain)

        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.vertical_layout_one = QtWidgets.QVBoxLayout()
        self.vertical_layout_two = QtWidgets.QVBoxLayout()
        self.vertical_layout_three = QtWidgets.QVBoxLayout()
        self.horizontal_layout.addWidget(self.button_main_menu)
        self.horizontal_layout.addWidget(self.button_finish_setting_values)
        #self.horizontal_layout.addWidget(self.container, 1)
        self.horizontal_layout.addLayout(self.vertical_layout_one)
        self.horizontal_layout.addLayout(self.vertical_layout_two)
        self.horizontal_layout.addLayout(self.vertical_layout_three)
        
        self.vertical_layout_one.addWidget(self.label_azimuth_max)
        self.vertical_layout_one.addWidget(self.label_azimuth_min)
        self.vertical_layout_one.addWidget(self.label_elevation_max)
        self.vertical_layout_one.addWidget(self.label_elevation_min)
        self.vertical_layout_one.addWidget(self.label_step_change)
        self.vertical_layout_one.addWidget(self.label_scan_frequency)
        self.vertical_layout_one.addWidget(self.label_samples_orientation)
        self.vertical_layout_two.addWidget(self.slider_azimuth_max)
        self.vertical_layout_two.addWidget(self.slider_azimuth_min)
        self.vertical_layout_two.addWidget(self.slider_elevation_max)
        self.vertical_layout_two.addWidget(self.slider_elevation_min)
        self.vertical_layout_two.addWidget(self.slider_step_change)
        self.vertical_layout_two.addWidget(self.slider_scan_frequency)
        self.vertical_layout_two.addWidget(self.slider_samples_orientation)
        self.vertical_layout_three.addWidget(self.lcd_azimuth_max)
        self.vertical_layout_three.addWidget(self.lcd_azimuth_min)
        self.vertical_layout_three.addWidget(self.lcd_elevation_max)
        self.vertical_layout_three.addWidget(self.lcd_elevation_min)
        self.vertical_layout_three.addWidget(self.lcd_step_change)
        self.vertical_layout_three.addWidget(self.lcd_scan_frequency)
        self.vertical_layout_three.addWidget(self.lcd_samples_orientation)
        self.setWindowTitle("Graph Console")
        
    def azimuth_max_change(self):
        size = self.slider_azimuth_max.value()
        self.lcd_azimuth_max.display(size)
    
    def azimuth_min_change(self):
        size = self.slider_azimuth_min.value()
        self.lcd_azimuth_min.display(size)
    
    def elevation_max_change(self):
        size = self.slider_elevation_max.value()
        self.lcd_elevation_max.display(size)
    
    def elevation_min_change(self):
        size = self.slider_elevation_min.value()
        self.lcd_elevation_min.display(size)
    
    def scan_frequency_change(self):
        size = self.slider_scan_frequency.value()
        self.lcd_scan_frequency.display(size)
    
    def step_change_change(self):
        size = self.slider_step_change.value()
        self.lcd_step_change.display(size)
    
    def samples_orientation_change(self):
        size = self.slider_samples_orientation.value()
        self.lcd_samples_orientation.display(size)
    
    def button_main_menu_click(self):
        self.main_menu = GraphConsole()
        self.main_menu.show()
        self.main_menu.setAttribute(Qt.WA_DeleteOnClose)
        self.close()
    
    def button_finish_setting_values_click(self):
        self.finish_setting_values = GraphConsole()
        self.finish_setting_values.show()
        t_a = self.lcd_azimuth_min.value()
        t_b = self.lcd_azimuth_max.value()
        t_c = self.lcd_elevation_min.value()
        t_d = self.lcd_elevation_max.value()
        t_f = self.lcd_step_change.value()
        t_g = self.lcd_samples_orientation.value()
        t_h = self.lcd_scan_frequency.value()
        temp_string = f'-a={t_a},{t_b}-e={t_c},{t_d}-s{t_f}.'
        self.serial.write(temp_string.encode())
        self.finish_setting_values.setAttribute(Qt.WA_DeleteOnClose)
        self.close()