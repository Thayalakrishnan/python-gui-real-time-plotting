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


from realtimeplotter.plotter import Plotter


def CreateLCD(lcd_object_name, lcd_has_decimal_point, lcd_size_width, lcd_size_height) -> QtWidgets.QLCDNumber:
    lcd  = QtWidgets.QLCDNumber()
    lcd.setFrameShape(QtWidgets.QFrame.NoFrame)
    lcd.setSmallDecimalPoint(lcd_has_decimal_point)
    lcd.setObjectName(lcd_object_name)
    lcd.setFixedSize(lcd_size_width, lcd_size_height)
    return lcd

def CreateLabel(label_text, label_size_width, label_size_height) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel()
    label.setFixedSize(label_size_width, label_size_height)
    label.setFrameShape(QtWidgets.QFrame.StyledPanel)
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setText(label_text)
    return label

""" DetailedGraphWidget
    This class creates an instance of the graphing console
    the graphing console is a much more detailed scanning conole that provides real time 
    information regarding the current scan. it is instantiated right after triggering one of
    customs can, quick scan or deep scan
    
    This Class subclasses the QtWidgets to create an instance 
"""
''' Generate the Graphing Console '''
class DetailedGraphWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DetailedGraphWidget, self).__init__(parent)
        ''' Widgets '''
        self.run_scan = QtWidgets.QPushButton(text="Run Scan")
        self.run_scan.setFixedSize(120,50)
        self.stop_scan = QtWidgets.QPushButton(text="Stop Scan")
        self.stop_scan.setFixedSize(120,50)
                
        self.lcd_acc = CreateLCD("lcd_acc", False, 120, 50)
        self.lcd_gyr = CreateLCD("lcd_gyr", False, 120, 50)
        self.lcd_mag = CreateLCD("lcd_mag", False, 120, 50)
        self.lcd_azi = CreateLCD("lcd_azi", False, 120, 50)
        self.lcd_ele = CreateLCD("lcd_ele", False, 120, 50)
        self.lcd_dis = CreateLCD("lcd_dis", False, 120, 50)
        
        ''' Graphing '''
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.graph_container = QtWidgets.QWidget.createWindowContainer(graph)
        self.graph_container.setMinimumSize(QSize(screenSize.width() / 2, screenSize.height() / 1.5))
        self.graph_container.setMaximumSize(screenSize)
        self.graph_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_container.setFocusPolicy(Qt.StrongFocus)
        self.modified_graph = Plotter(graph)
        
        ''' Labels '''       
        self.label_acc = CreateLabel("Accelerometer", 120, 50)
        self.label_gyr = CreateLabel("Gyroscope", 120, 50)
        self.label_mag = CreateLabel("Magnetometer", 120, 50)
        self.label_azi = CreateLabel("Azimuth", 120, 50)
        self.label_ele = CreateLabel("Elevation", 120, 50)
        self.label_dis = CreateLabel("Distance", 120, 50)


        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.graph_container, 1)
        
        self.vertical_layout = QtWidgets.QVBoxLayout()
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

