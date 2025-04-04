from . import dependencies
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox


class NenSDependencyLoader:
    def __init__(self, iface):
        self.iface = iface
        dependencies.ensure_everything_installed()
        dependencies.check_importability()

    def initGui(self):
        self.action = QAction("Info", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        QMessageBox.information(None, "N&S Dependency Loader", "Info")
