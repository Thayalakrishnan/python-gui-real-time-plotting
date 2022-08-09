""" @package RangeFinder
  This package contains all the classes that are used to create an instance of the GUI
  The classes dont take any input and run off of each other. Button input triggers the 
 instance of one of these classes as every class generates a new window, except the plotting 
"""
from PyQt5.QtCore import QSize, Qt

from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtDatavisualization import Q3DScatter


from realtimeplotter.plotter import Plotter

from realtimeplotter.helpers import HBoxLayoutHelper, LCDWidgetHelper, LabelWidgetHelper


def CreateLCD(
    lcd_object_name, lcd_has_decimal_point, size_width, size_height
) -> QLCDNumber:
    lcd = QLCDNumber()
    lcd.setFrameShape(QFrame.NoFrame)
    lcd.setSmallDecimalPoint(lcd_has_decimal_point)
    lcd.setObjectName(lcd_object_name)
    lcd.setFixedSize(size_width, size_height)
    return lcd


def CreateLabel(label_text, label_size_width, label_size_height) -> QLabel:
    label = QLabel()
    label.setFixedSize(label_size_width, label_size_height)
    label.setFrameShape(QFrame.StyledPanel)
    label.setAlignment(Qt.AlignCenter)
    label.setText(label_text)
    return label


def CreateLCDLabelHBox(lcd_widget, label_widget) -> QLabel:
    h_lay = QHBoxLayout()
    h_lay.addWidget(lcd_widget)
    h_lay.addWidget(label_widget)
    return h_lay


""" DetailedGraphWidget
    This class creates an instance of the graphing console
    the graphing console is a much more detailed scanning conole that provides real time 
    information regarding the current scan. it is instantiated right after triggering one of
    customs can, quick scan or deep scan
    
    This Class subclasses the to create an instance 
"""
""" Generate the Graphing Console """


class DetailedGraphWidget(QWidget):
    def __init__(self, parent=None):
        super(DetailedGraphWidget, self).__init__(parent)
        """ Widgets """
        self.run_scan = QPushButton(text="Run Scan")
        self.run_scan.setFixedSize(120, 50)
        self.stop_scan = QPushButton(text="Stop Scan")
        self.stop_scan.setFixedSize(120, 50)

        self.lcd_acc = LCDWidgetHelper("lcd_acc", False, 120, 50)
        self.lcd_gyr = LCDWidgetHelper("lcd_gyr", False, 120, 50)
        self.lcd_mag = LCDWidgetHelper("lcd_mag", False, 120, 50)
        self.lcd_azi = LCDWidgetHelper("lcd_azi", False, 120, 50)
        self.lcd_ele = LCDWidgetHelper("lcd_ele", False, 120, 50)
        self.lcd_dis = LCDWidgetHelper("lcd_dis", False, 120, 50)

        """ Graphing """
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.graph_container = QWidget.createWindowContainer(graph)
        self.graph_container.setMinimumSize(QSize(300, 300))
        self.graph_container.setMaximumSize(screenSize)
        self.graph_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_container.setFocusPolicy(Qt.StrongFocus)
        self.modified_graph = Plotter(graph)

        """ Labels """
        self.label_acc = LabelWidgetHelper("Accelerometer", 120, 50)
        self.label_gyr = LabelWidgetHelper("Gyroscope", 120, 50)
        self.label_mag = LabelWidgetHelper("Magnetometer", 120, 50)
        self.label_azi = LabelWidgetHelper("Azimuth", 120, 50)
        self.label_ele = LabelWidgetHelper("Elevation", 120, 50)
        self.label_dis = LabelWidgetHelper("Distance", 120, 50)

        """ Layout """
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.graph_container, 1)

        self.vertical_layout_two = QVBoxLayout()
        self.vertical_layout.addLayout(self.vertical_layout_two, 2)

        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.run_scan, self.stop_scan])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_acc, self.lcd_acc])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_gyr, self.lcd_gyr])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_mag, self.lcd_mag])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_azi, self.lcd_azi])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_ele, self.lcd_ele])
        )
        self.vertical_layout_two.addLayout(
            HBoxLayoutHelper([self.label_dis, self.lcd_dis])
        )
        self.setWindowTitle("Graph Console")
