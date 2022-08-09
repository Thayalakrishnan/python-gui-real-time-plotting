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
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QGroupBox,
                            QFontComboBox, QFrame, QHBoxLayout, QLabel, 
                            QLCDNumber, QMainWindow, QPushButton, 
                            QSizePolicy, QSlider, QVBoxLayout, QWidget, QStyleFactory, QStyle)
from qtpy.QtDatavisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
                                      QAbstract3DAxis, QAbstract3DGraph,
                                      QAbstract3DSeries, QCustom3DItem,
                                      QScatter3DSeries, QScatterDataItem,
                                      QScatterDataProxy, QValue3DAxis,
                                      QValue3DAxisFormatter)


from realtimeplotter.detailed_graph_widget import DetailedGraphWidget
from realtimeplotter.helpers import LCDWidgetHelper, LabelWidgetHelper, SliderWidgetHelper, HBoxLayoutHelper





"""
Custom scan boundary values
"""
AZIMUTH_MIN_LOW = 30
AZIMUTH_MIN_HIGH = 155
AZIMUTH_STEP = 1

AZIMUTH_MAX_LOW = 35
AZIMUTH_MAX_HIGH = 160
AZIMUTH_STEP = 1

ELEVATE_MIN_LOW = -60
ELEVATE_MIN_HIGH = 55
ELEVATE_STEP = 1

ELEVATE_MAX_LOW = -55
ELEVATE_MAX_HIGH = 60
ELEVATE_STEP = 1

STEP_CHANGE_LOW = 5
STEP_CHANGE_HIGH = 200
STEP_CHANGE_STEP = 1

SAMPLE_FREQUENCY_LOW = 1
SAMPLE_FREQUENCY_HIGH = 100
SAMPLE_FREQUENCY_STEP = 1

SAMPLES_PER_ORIENTATION_LOW = 3
SAMPLES_PER_ORIENTATION_HIGH = 10
SAMPLES_PER_ORIENTATION_STEP = 1



""" CustomScanWidget
    This class creates an instance of the custom scanning console
    the custom scan console houses sliders that allow the user to create a custom scan
    once the user is happy with the paramters, they hit proceed which will then pull the values
    and send them to the board to initialise the scan
    
    This Class subclasses the QtWidgets to create an instance
"""

class CustomScanWidget(QtWidgets.QWidget):
    """ The constructor."""
    def __init__(self, parent=None):
        super(CustomScanWidget, self).__init__(parent)
        ''' Widgets '''
        self.serial = QtSerialPort.QSerialPort('COM4',baudRate=QtSerialPort.QSerialPort.Baud9600)
        
        self.button_finish_setting_values = QtWidgets.QPushButton(text="Proceed")
        self.button_finish_setting_values.setFixedSize(120,50)
        
        self.button_main_menu = QtWidgets.QPushButton(text="Main Menu")
        self.button_main_menu.setFixedSize(120,50)
                
        # configure global application font
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setKerning(False)
        self.setFont(font)
                
        '''labels'''
        self.label_azimuth_min = LabelWidgetHelper("Azimuth Min", 120, 50)
        self.label_azimuth_max = LabelWidgetHelper("Azimuth Max", 120, 50)
        self.label_elevation_min = LabelWidgetHelper("Elevation Max", 120, 50)
        self.label_elevation_max = LabelWidgetHelper("Elevation Max", 120, 50)
        self.label_step_change = LabelWidgetHelper("Step Change", 120, 50)
        self.label_scan_frequency = LabelWidgetHelper("Scan Frequency", 120, 50)
        self.label_samples_orientation = LabelWidgetHelper("Samples/Orientation", 120, 50)
        
        '''sliders'''
        self.slider_azimuth_min = SliderWidgetHelper(250, 50, AZIMUTH_MIN_LOW, AZIMUTH_MIN_HIGH, AZIMUTH_STEP)
        self.slider_azimuth_max = SliderWidgetHelper(250, 50, AZIMUTH_MAX_LOW, AZIMUTH_MAX_HIGH, AZIMUTH_STEP)
        self.slider_elevation_min = SliderWidgetHelper(250, 50, ELEVATE_MIN_LOW, ELEVATE_MIN_HIGH, ELEVATE_STEP)
        self.slider_elevation_max = SliderWidgetHelper(250, 50, ELEVATE_MAX_LOW, ELEVATE_MAX_HIGH, ELEVATE_STEP)
        self.slider_step_change = SliderWidgetHelper(250, 50, STEP_CHANGE_LOW, STEP_CHANGE_HIGH, STEP_CHANGE_STEP)
        self.slider_scan_frequency = SliderWidgetHelper(250, 50, SAMPLE_FREQUENCY_LOW, SAMPLE_FREQUENCY_HIGH, SAMPLE_FREQUENCY_STEP)
        self.slider_samples_orientation = SliderWidgetHelper(250, 50, SAMPLES_PER_ORIENTATION_LOW, SAMPLES_PER_ORIENTATION_HIGH, SAMPLES_PER_ORIENTATION_STEP)
        
        ''' LCDs '''
        self.lcd_azimuth_min = LCDWidgetHelper("lcd_azi_min", False, 120, 50)
        self.lcd_azimuth_max = LCDWidgetHelper("lcd_azi_max", False, 120, 50)
        self.lcd_elevation_min = LCDWidgetHelper("lcd_ele_min", False, 120, 50)
        self.lcd_elevation_max = LCDWidgetHelper("lcd_ele_max", False, 120, 50)
        self.lcd_step_change = LCDWidgetHelper("lcd_step_change", False, 120, 50)
        self.lcd_scan_frequency = LCDWidgetHelper("lcd_scan_freq", False, 120, 50)
        self.lcd_samples_orientation = LCDWidgetHelper("lcd_samp_ori", False, 120, 50)





        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        
        self.vertical_layout_one = QtWidgets.QVBoxLayout()
        self.vertical_layout_two = QtWidgets.QVBoxLayout()
        
        self.horizontal_layout.addLayout(self.vertical_layout_one)
        self.horizontal_layout.addLayout(self.vertical_layout_two)       
        
        self.vertical_layout_one.addWidget(self.button_main_menu)
        self.vertical_layout_one.addWidget(self.button_finish_setting_values)
        
        ''' Add Widget '''
        #self.vertical_layout_two.addLayout(HBoxLayoutHelper([self.label_azimuth_min, self.slider_azimuth_min, self.lcd_azimuth_min]))
        #self.vertical_layout_two.addLayout(HBoxLayoutHelper([self.label_azimuth_max, self.slider_azimuth_max, self.lcd_azimuth_max]))
        #self.vertical_layout_two.addLayout(HBoxLayoutHelper([self.label_elevation_min, self.slider_elevation_min, self.lcd_elevation_min]))
        #self.vertical_layout_two.addLayout(HBoxLayoutHelper([self.label_elevation_max, self.slider_elevation_max, self.lcd_elevation_max]))
        
        
        self.GBox_Azimuth = QGroupBox(self, title="Azimuth")
        self.Vbox_Azimuth = QtWidgets.QVBoxLayout()
        self.GBox_Azimuth.setLayout(self.Vbox_Azimuth)
        self.Vbox_Azimuth.addLayout(HBoxLayoutHelper([self.label_azimuth_min, self.slider_azimuth_min, self.lcd_azimuth_min]))
        self.Vbox_Azimuth.addLayout(HBoxLayoutHelper([self.label_azimuth_max, self.slider_azimuth_max, self.lcd_azimuth_max]))

        self.GBox_Elevation = QGroupBox(self, title="Elevation")
        self.Vbox_Elevation = QtWidgets.QVBoxLayout()
        self.GBox_Elevation.setLayout(self.Vbox_Elevation)
        self.Vbox_Elevation.addLayout(HBoxLayoutHelper([self.label_elevation_min, self.slider_elevation_min, self.lcd_elevation_min]))
        self.Vbox_Elevation.addLayout(HBoxLayoutHelper([self.label_elevation_max, self.slider_elevation_max, self.lcd_elevation_max]))

        self.GBox_StepChange = QGroupBox(self, title="Step Change")
        self.Vbox_StepChange = QtWidgets.QVBoxLayout()        
        self.GBox_StepChange.setLayout(self.Vbox_StepChange)
        self.Vbox_StepChange.addLayout(HBoxLayoutHelper([self.label_step_change, self.slider_step_change, self.lcd_step_change]))
        
        self.GBox_ScanFrequency = QGroupBox(self, title="Scan Frequency")
        self.Vbox_ScanFrequency = QtWidgets.QVBoxLayout()        
        self.GBox_ScanFrequency.setLayout(self.Vbox_ScanFrequency)
        self.Vbox_ScanFrequency.addLayout(HBoxLayoutHelper([self.label_scan_frequency, self.slider_scan_frequency, self.lcd_scan_frequency]))
        
        self.GBox_SamplesPerOrientaiton = QGroupBox(self, title="Samples Per Orientaiton")
        self.Vbox_SamplesPerOrientaiton = QtWidgets.QVBoxLayout()        
        self.GBox_SamplesPerOrientaiton.setLayout(self.Vbox_SamplesPerOrientaiton)
        self.Vbox_SamplesPerOrientaiton.addLayout(HBoxLayoutHelper([self.label_samples_orientation, self.slider_samples_orientation, self.lcd_samples_orientation]))
        
        
        
        self.vertical_layout_two.addWidget(self.GBox_Azimuth)
        self.vertical_layout_two.addWidget(self.GBox_Elevation)
        self.vertical_layout_two.addWidget(self.GBox_StepChange)
        self.vertical_layout_two.addWidget(self.GBox_ScanFrequency)
        self.vertical_layout_two.addWidget(self.GBox_SamplesPerOrientaiton)
        
        
        self.setWindowTitle("Graph Console")
        
    """ Azimuth Max Slider
      @param self The object pointer."""
    def azimuth_max_change(self):
        size = self.slider_azimuth_max.value()
        self.lcd_azimuth_max.display(size)
    """ Azimuth Min Slider.
      @param self The object pointer."""
    def azimuth_min_change(self):
        size = self.slider_azimuth_min.value()
        self.lcd_azimuth_min.display(size)
    """ Elevation Max Slider.
      @param self The object pointer."""
    def elevation_max_change(self):
        size = self.slider_elevation_max.value()
        self.lcd_elevation_max.display(size)
    """ Azimuth Max Slider.
      @param self The object pointer."""
    def elevation_min_change(self):
        size = self.slider_elevation_min.value()
        self.lcd_elevation_min.display(size)
    """ Elevation Min Slider.
      @param self The object pointer."""
    def scan_frequency_change(self):
        size = self.slider_scan_frequency.value()
        self.lcd_scan_frequency.display(size)
    """ Step Change Slider.
      @param self The object pointer."""
    def step_change_change(self):
        size = self.slider_step_change.value()
        self.lcd_step_change.display(size)
    """ Samples per orientaion Slider.
      @param self The object pointer."""
    def samples_orientation_change(self):
        size = self.slider_samples_orientation.value()
        self.lcd_samples_orientation.display(size)
    """ Button for main menu
      @param self The object pointer."""
    def button_main_menu_click(self):
        self.main_menu = DetailedGraphWidget()
        self.main_menu.show()
        self.main_menu.setAttribute(Qt.WA_DeleteOnClose)
        self.close()
    """ Button to trigger the beggining of the custom scan. takes the values here and sends them via serial to modify the scan
      @param self The object pointer."""
    def button_finish_setting_values_click(self):
        self.finish_setting_values = DetailedGraphWidget()
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

