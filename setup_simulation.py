import sys
from PyQt5.QtWidgets import QApplication

from simulation.plot_simulation import LivePlotSimulator
from realtimeplotter.theme import ApplicationTheme


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(ApplicationTheme())
    w = LivePlotSimulator()

    w.show()
    sys.exit(app.exec_())