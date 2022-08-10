"""
DetailedGraphWidget
"""
from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from PyQt5.QtDataVisualization import Q3DScatter

from realtimeplotter.plotter import Plotter
from realtimeplotter.helpers import HBoxLayoutHelper, LCDWidgetHelper, LabelWidgetHelper

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

        """
        Graphing 
        """
        self.graph_instance = Plotter()
        self.graph_container = self.graph_instance.graph_container

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
