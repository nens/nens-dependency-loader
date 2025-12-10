from . import dependencies
from pathlib import Path
from pyplugin_installer.installer_data import plugins
from pyplugin_installer.version_compare import compareVersions
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QMessageBox

import pyplugin_installer


PLUGIN_DIR = Path(__file__).parent


def check_for_update():
    pyplugin_installer.instance().fetchAvailablePlugins(True)
    plugin = plugins.all()["nens_dependency_loader"]
    if not plugin:
        return

    if compareVersions(plugin["version_installed"], plugin["version_available"]) == 2:
        pyplugin_installer.instance().installPlugin("nens_dependency_loader")


class NenSDependencyLoader:
    def __init__(self, iface):
        check_for_update()
        self.iface = iface
        dependencies.ensure_everything_installed()
        dependencies.check_importability()

    def initGui(self):
        self.action = QAction(
            QIcon(str(PLUGIN_DIR / "icon.svg")), "Info", self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("N&&S Dependency Loader", self.action)

    def unload(self):
        self.iface.removePluginMenu("N&&S Dependency Loader", self.action)
        del self.action

    def run(self):
        versions = "no constraints file detected"
        with open(str(PLUGIN_DIR / "constraints.txt"), "r") as file:
            versions = file.read()
        QMessageBox.information(None, "N&S Dependency Loader", versions)
