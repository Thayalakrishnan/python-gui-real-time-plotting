""" @package RangeFinder
  This package contains all the classes that are used to create an instance of the GUI
  The classes dont take any input and run off of each other. Button input triggers the 
 instance of one of these classes as every class generates a new window, except the plotting 
"""
import sys
from PyQt5.QtWidgets import QApplication
from realtimeplotter.real_time_plotter import RealTimePlotter
from realtimeplotter.theme import ApplicationTheme


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setPalette(ApplicationTheme())
    
    w = RealTimePlotter()
    
    ''' 
    Initialise the Sliders 
    '''
    w.button_quick_scan.clicked.connect(w.button_quick_scan_click)
    w.button_deep_scan.clicked.connect(w.button_deep_scan_click)
    w.button_custom_scan.clicked.connect(w.button_custom_scan_click)
    w.button_calibrate.clicked.connect(w.button_calibrate_click)
    w.button_ptu_control.clicked.connect(w.button_ptu_control_click)
    w.button_help.clicked.connect(w.button_help_click)
    
    w.show()
    sys.exit(app.exec_())