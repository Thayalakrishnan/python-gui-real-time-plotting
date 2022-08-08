""" @module 
plotter
"""
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

""" This class handles the entire plotting infrastructure. 
  The class is instantiated within another window and can take in data to be plotted.
  The graph is a scatter plot and is pannable and zoomable. """
  

class RangeFinderPlotter(QObject):
    def __init__(self, scatter):
        super(RangeFinderPlotter, self).__init__()
        self.graph = scatter  # graph instance passed in as arument
        self.m_fontSize = 12
        self.m_style = QAbstract3DSeries.MeshSphere
        self.m_smooth = True
        self.plot_timer = QTimer()
        
        """ Graph Theme """ 
        customTheme = self.graph.activeTheme()
        customTheme.setAmbientLightStrength(0.3)
        customTheme.setBackgroundColor(QColor(QColorConstants.White))
        customTheme.setBackgroundEnabled(False)
        customTheme.setBaseColors([QColorConstants.Red,QColorConstants.DarkRed,QColorConstants.Magenta])
        customTheme.setColorStyle(Q3DTheme.ColorStyleUniform)
        customTheme.setFont(QFont("Arial"))
        customTheme.setGridEnabled(True)
        customTheme.setGridLineColor(QColor(QColorConstants.White))
        customTheme.setHighlightLightStrength(7.0)
        
        # labels
        customTheme.setLabelBackgroundColor(QColor(QColorConstants.Black))
        customTheme.setLabelBackgroundEnabled(True)
        customTheme.setLabelBorderEnabled(True)
        customTheme.setLabelTextColor(QColor(QColorConstants.White))
        #light
        customTheme.setLightColor(QColor(QColorConstants.White))
        customTheme.setLightStrength(6.0)
        customTheme.setMultiHighlightColor(QColor(QColorConstants.White))
        customTheme.setSingleHighlightColor(QColor(QColorConstants.White))
        
        
        #window 
        #customTheme.setWindowColor(QColor(QColorConstants.Black)) 
        customTheme.setWindowColor(QColor(QColorConstants.White))
        self.graph.activeTheme().setType(Q3DTheme.ThemeUserDefined)
        
        ''' shadow quality '''
        font = self.graph.activeTheme().font()
        font.setPointSize(12.0)
        self.graph.activeTheme().setFont(QFont("Arial"))
        self.graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)
        self.graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetIsometricRight)
        self.graph.scene().activeCamera().setZoomLevel(150.0)
        proxy = QScatterDataProxy()
        series = QScatter3DSeries(proxy)
        # this is how an indidiaul point should be labelled when it is clicked on 
        # so the label here will be dipslayed in the graph view when a plotted item is clicked
        series.setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
        series.setMeshSmooth(self.m_smooth)
        series.setItemSize(0.01)
        self.graph.addSeries(series)
        
        """ Configure axis"""
        xaxis_proxy = QValue3DAxisFormatter()
        xaxis = QValue3DAxis(xaxis_proxy)
        xaxis.setLabelFormat("%.2f mm")
        xaxis.setSegmentCount(5)
        xaxis.setSubSegmentCount(2)
        xaxis.setTitle("X axis")
        xaxis.setTitleVisible(True)
        self.graph.addAxis(xaxis)
        
        # configure y axis
        yaxis_proxy = QValue3DAxisFormatter()
        yaxis = QValue3DAxis(yaxis_proxy)
        yaxis.setLabelFormat("%.2f mm")
        yaxis.setSegmentCount(5)
        yaxis.setSubSegmentCount(2)
        yaxis.setTitle("Y axis")
        yaxis.setTitleVisible(True)
        self.graph.addAxis(yaxis)
        
        # configure z axis
        zaxis_proxy = QValue3DAxisFormatter()
        zaxis = QValue3DAxis(zaxis_proxy)
        zaxis.setLabelFormat("%.2f mm")
        zaxis.setSegmentCount(5)
        zaxis.setSubSegmentCount(2)
        zaxis.setTitle("Z axis")
        zaxis.setTitleVisible(True)
        self.graph.addAxis(zaxis)
        
        # title axis??
        title_proxy = QValue3DAxisFormatter()
        taxis = QValue3DAxis(title_proxy)
        taxis.setTitle("Range finder")
        taxis.setTitleVisible(True)
        
        ''' shadow quality '''
        self.graph.setAxisX(xaxis)
        self.graph.setAxisY(yaxis)
        self.graph.setAxisZ(zaxis)
        self.graph.setTitle("Range finder")
        self.graph.axisX().setRange(-1500,1500)
        self.graph.axisY().setRange(-1500,1500)
        self.graph.axisZ().setRange(0,3000)
        self.graph.axisX().setTitle("X axis (azimuth)")
        self.graph.axisY().setTitle("Y axis (elevation)")
        self.graph.axisZ().setTitle("Z axis (depth/range)")
        self.graph.seriesList()[0].setMesh(self.m_style)
        self.graph.seriesList()[0].setMeshSmooth(self.m_smooth)
        self.graph.setAspectRatio(1.0)
    
    """ Function to plot the given data point
      @param self The object pointer"""
    def addCustomItem(self, point):
        new_item = QCustom3DItem()
        new_item.setMeshFile('sphere.obj')
        new_item.setScaling(QVector3D(0.005,0.005,0.005))
        new_item.setPosition(point)
        self.graph.addCustomItem(new_item)

