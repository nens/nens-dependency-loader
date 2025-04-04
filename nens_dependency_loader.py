from . import dependencies
from pathlib import Path
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon


PLUGIN_DIR = Path(__file__).parent


class NenSDependencyLoader:
    def __init__(self, iface):
        self.iface = iface
        dependencies.ensure_everything_installed()
        dependencies.check_importability()

    def initGui(self):
        self.action = QAction(
            QIcon(str(PLUGIN_DIR / "icon.svg")), "Info", self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        QMessageBox.information(None, "N&S Dependency Loader", "Info")
