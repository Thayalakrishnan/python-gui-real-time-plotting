"""
Plotter
This class handles the entire plotting infrastructure. 
The graph is a scatter plot and is pannable and zoomable. 
"""
from PyQt5.QtDataVisualization import (
    Q3DCamera,
    Q3DScatter,
    Q3DTheme,
    QAbstract3DGraph,
    QAbstract3DSeries,
    QScatter3DSeries,
    QScatterDataProxy,
    QValue3DAxis,
    QValue3DAxisFormatter,
    QScatterDataItem
)
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QTimer, QObject, QSize, Qt
from PyQt5.QtGui import QColor, QColorConstants, QFont



MESH_FILE_LOCATION = "C:\\dev\\github\\python-gui-real-time-plotting\\realtimeplotter\\sphere.obj"

AXIS_MIN = -20
AXIS_MAX = 20

X_AXIS_MIN = AXIS_MIN
X_AXIS_MAX = AXIS_MAX
Y_AXIS_MIN = AXIS_MIN
Y_AXIS_MAX = AXIS_MAX
Z_AXIS_MIN = AXIS_MIN
Z_AXIS_MAX = AXIS_MAX


def CreateAxisHelper(
    axis_proxy, axis_title, axis_title_visible, axis_segs, axis_subsegs
) -> QValue3DAxis:
    axis = QValue3DAxis(axis_proxy)
    axis.setLabelFormat("%d mm")
    axis.setSegmentCount(axis_segs)
    axis.setSubSegmentCount(axis_subsegs)
    axis.setTitle(axis_title)
    axis.setTitleVisible(axis_title_visible)
    return axis


class Plotter(QObject):
    def __init__(self):
        super(Plotter, self).__init__()
        self.graph = Q3DScatter()
        self.setUpUi()     
        
    def setUpUi(self):
        self.graph.setAspectRatio(1.0)
        self.graph_container = QWidget.createWindowContainer(self.graph)
        self.graph_container.setMinimumSize(QSize(500, 500))
        self.graph_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_container.setFocusPolicy(Qt.StrongFocus)
        self.set_graph_theme()
        self.set_shadows_axis()
        self.set_scatter_series()
        self.reset_graph()
        self.set_graph_axis()
        
    def add_new_item(self, pos):
        point = QScatterDataItem(pos)
        self.scatter_proxy.addItem(point)

    def reset_graph(self):
        self.scatter_proxy = QScatterDataProxy()
        self.scatter_series.setDataProxy(self.scatter_proxy)
        self.counter = 0
        
    
    def enable_rotation(self):
        self.plot_timer = QTimer()
        self.plot_timer.setInterval(10)
        self.plot_timer.timeout.connect(self.rotate_x_axis)
        self.plot_timer.start()

    def disable_rotation(self):
        self.plot_timer.stop()
    
    def rotate_x_axis(self):
        x_rot = self.graph.scene().activeCamera().xRotation()        
        self.graph.scene().activeCamera().setXRotation(x_rot + 0.5)
    
    def set_scatter_series(self):
        """
        set scatter series
        """
        self.scatter_series = QScatter3DSeries()
        self.scatter_series.setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
        self.scatter_series.setMesh(QAbstract3DSeries.MeshSphere)
        self.scatter_series.setMeshSmooth(True)
        self.scatter_series.setItemSize(0.1)
        self.scatter_series.setBaseColor(QColor(220, 20, 60))
        self.graph.addSeries(self.scatter_series)
        
    
    def set_graph_theme(self):
        """ Graph Theme """
        customTheme = self.graph.activeTheme()
        customTheme.setAmbientLightStrength(0.3)
        customTheme.setBackgroundColor(QColor(42, 42, 42))
        customTheme.setBackgroundEnabled(True)
        customTheme.setBackgroundEnabled(False)
        customTheme.setColorStyle(Q3DTheme.ColorStyleUniform)
        customTheme.setFont(QFont("Segoe UI"))
        customTheme.setGridEnabled(True)
        customTheme.setGridLineColor(QColor(QColorConstants.Red))
        customTheme.setHighlightLightStrength(7.0)

        # labels
        customTheme.setLabelBackgroundColor(QColor(42, 42, 42))
        customTheme.setLabelBackgroundEnabled(True)
        customTheme.setLabelBorderEnabled(False)
        customTheme.setLabelTextColor(QColor(QColorConstants.White))

        # light
        customTheme.setLightColor(QColor(QColorConstants.White))
        customTheme.setLightStrength(6.0)
        customTheme.setMultiHighlightColor(QColor(QColorConstants.White))
        customTheme.setSingleHighlightColor(QColor(QColorConstants.White))

        # window
        customTheme.setWindowColor(QColor(42, 42, 42))

        """ font """
        font = self.graph.activeTheme().font()
        font.setPointSize(24.0)
        self.graph.activeTheme().setFont(QFont("Segoe UI"))
    
    def set_shadows_axis(self):
        """ 
        shadows and camera quality 
        """
        self.graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)
        self.graph.scene().activeCamera().setCameraPreset(
            Q3DCamera.CameraPresetIsometricRight
        )
        self.graph.scene().activeCamera().setZoomLevel(150.0)
    
    def set_graph_axis(self):
        """ Configure axis"""
        self.xaxis_proxy = QValue3DAxisFormatter()
        self.xaxis = CreateAxisHelper(self.xaxis_proxy, "X axis (azimuth)", True, 5, 2)
        self.graph.addAxis(self.xaxis)
        self.graph.setAxisX(self.xaxis)

        self.yaxis_proxy = QValue3DAxisFormatter()
        self.yaxis = CreateAxisHelper(self.yaxis_proxy, "Y axis (elevation)", True, 5, 2)
        self.graph.addAxis(self.yaxis)
        self.graph.setAxisY(self.yaxis)

        self.zaxis_proxy = QValue3DAxisFormatter()
        self.zaxis = CreateAxisHelper(self.zaxis_proxy, "Z axis (depth/range)", True, 5, 2)
        self.graph.addAxis(self.zaxis)
        self.graph.setAxisZ(self.zaxis)

        # title axis??
        self.title_proxy = QValue3DAxisFormatter()
        self.taxis = QValue3DAxis(self.title_proxy)
        self.taxis.setTitle("Range finder")
        self.taxis.setTitleVisible(True)

        """ Axis Range """
        self.graph.setTitle("Range finder")
        self.graph.axisX().setRange(X_AXIS_MIN, X_AXIS_MAX)
        self.graph.axisY().setRange(Y_AXIS_MIN,Y_AXIS_MAX)
        self.graph.axisZ().setRange(Z_AXIS_MIN,Z_AXIS_MAX)