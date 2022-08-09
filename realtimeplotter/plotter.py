""" @module 
plotter
"""
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

""" This class handles the entire plotting infrastructure. 
  The class is instantiated within another window and can take in data to be plotted.
  The graph is a scatter plot and is pannable and zoomable. """


def CreateAxis(
    axis_proxy, axis_title, axis_title_visible, axis_segs, axis_subsegs
) -> QValue3DAxis:
    axis = QValue3DAxis(axis_proxy)
    axis.setLabelFormat("%.2f mm")
    axis.setSegmentCount(axis_segs)
    axis.setSubSegmentCount(axis_subsegs)
    axis.setTitle(axis_title)
    axis.setTitleVisible(axis_title_visible)
    return axis


class Plotter(QObject):
    def __init__(self, scatter):
        super(Plotter, self).__init__()
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
        customTheme.setBaseColors(
            [QColorConstants.Red, QColorConstants.DarkRed, QColorConstants.Magenta]
        )
        customTheme.setColorStyle(Q3DTheme.ColorStyleUniform)
        customTheme.setFont(QFont("Arial"))
        customTheme.setGridEnabled(True)
        customTheme.setGridLineColor(QColor(QColorConstants.White))
        customTheme.setHighlightLightStrength(7.0)

        # labels
        customTheme.setLabelBackgroundColor(QColor(QColorConstants.Black))
        customTheme.setLabelBackgroundEnabled(True)
        customTheme.setLabelBorderEnabled(True)
        customTheme.setLabelTextColor(QColor(QColorConstants.Red))

        # light
        customTheme.setLightColor(QColor(QColorConstants.White))
        customTheme.setLightStrength(6.0)
        customTheme.setMultiHighlightColor(QColor(QColorConstants.White))
        customTheme.setSingleHighlightColor(QColor(QColorConstants.White))

        # window
        # customTheme.setWindowColor(QColor(QColorConstants.Black))
        customTheme.setWindowColor(QColor(QColorConstants.White))
        self.graph.activeTheme().setType(Q3DTheme.ThemeUserDefined)

        """ font """
        font = self.graph.activeTheme().font()
        font.setPointSize(12.0)
        self.graph.activeTheme().setFont(QFont("Arial"))

        """ shadow quality """
        self.graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)
        self.graph.scene().activeCamera().setCameraPreset(
            Q3DCamera.CameraPresetIsometricRight
        )
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
        self.xaxis_proxy = QValue3DAxisFormatter()
        self.xaxis = CreateAxis(self.xaxis_proxy, "X axis (azimuth)", True, 5, 2)
        self.graph.addAxis(self.xaxis)
        self.graph.setAxisX(self.xaxis)

        self.yaxis_proxy = QValue3DAxisFormatter()
        self.yaxis = CreateAxis(self.yaxis_proxy, "Y axis (elevation)", True, 5, 2)
        self.graph.addAxis(self.yaxis)
        self.graph.setAxisY(self.yaxis)

        self.zaxis_proxy = QValue3DAxisFormatter()
        self.zaxis = CreateAxis(self.zaxis_proxy, "Z axis (depth/range)", True, 5, 2)
        self.graph.addAxis(self.zaxis)
        self.graph.setAxisZ(self.zaxis)

        # title axis??
        self.title_proxy = QValue3DAxisFormatter()
        self.taxis = QValue3DAxis(self.title_proxy)
        self.taxis.setTitle("Range finder")
        self.taxis.setTitleVisible(True)

        """ Axis Range """
        self.graph.setTitle("Range finder")
        self.graph.axisX().setRange(-1500, 1500)
        self.graph.axisY().setRange(-1500, 1500)
        self.graph.axisZ().setRange(0, 3000)

        self.graph.seriesList()[0].setMesh(self.m_style)
        self.graph.seriesList()[0].setMeshSmooth(self.m_smooth)
        self.graph.setAspectRatio(1.0)

    """ Function to plot the given data point
      @param self The object pointer"""

    def addCustomItem(self, point):
        print("[addCustomItem]")
        print(point)
        new_item = QCustom3DItem()
        new_item.setMeshFile("C:\\dev\\github\\python-gui-real-time-plotting\\realtimeplotter\\sphere.obj")
        # new_item.setScaling(QVector3D(0.005, 0.005, 0.005))
        new_item.setScaling(QVector3D(0.005, 0.005, 0.005))
        new_item.setPosition(point)
        self.graph.addCustomItem(new_item)
