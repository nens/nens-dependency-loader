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
        self.iface.addPluginToMenu("N&S Dependency Loader", self.action)

    def unload(self):
        self.iface.removePluginMenu("N&S Dependency Loader", self.action)
        del self.action

    def run(self):
        versions = "no constraints file detected"
        with open(str(PLUGIN_DIR / "constraints.txt"), "r") as file:
            versions = file.read()
        QMessageBox.information(None, "N&S Dependency Loader", versions)
