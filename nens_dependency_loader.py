from . import dependencies
from pathlib import Path
from pyplugin_installer.installer_data import plugins
from pyplugin_installer.version_compare import compareVersions
from qgis.core import QgsApplication
from qgis.core import QgsSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QCheckBox
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QGridLayout
from qgis.PyQt.QtWidgets import QLabel
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QPushButton
from qgis.PyQt.QtWidgets import QSizePolicy
from qgis.PyQt.QtWidgets import QSpacerItem

import pyplugin_installer

PLUGIN_DIR = Path(__file__).parent


def check_for_update():
    if not QgsSettings().value("nens_dependency_loader/auto_update", True):
        return

    try:
        pyplugin_installer.instance().fetchAvailablePlugins(True)
        plugin = plugins.all()["nens_dependency_loader"]
        if not plugin:
            return

        if (
            compareVersions(plugin["version_installed"], plugin["version_available"])
            == 2
        ):
            pyplugin_installer.instance().uninstallPlugin(
                "nens_dependency_loader", quiet=True
            )
            pyplugin_installer.instance().installPlugin("nens_dependency_loader")
    except:  # NOQA
        pass


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
        menu = self.iface.mainWindow().getPluginMenu("N&&S Dependency Loader")

        self.settings_action = QAction(
            QgsApplication.getThemeIcon("/processingAlgorithm.svg"),
            "Settings",
            self.iface.mainWindow(),
        )
        self.settings_action.triggered.connect(self.open_settings_dialog)
        menu.addAction(self.settings_action)

    def unload(self):
        self.iface.removePluginMenu("N&&S Dependency Loader", self.action)
        del self.action
        del self.settings_action

    def run(self):
        versions = "no constraints file detected"
        with open(str(PLUGIN_DIR / "constraints.txt"), "r") as file:
            versions = file.read()
        QMessageBox.information(None, "N&S Dependency Loader", versions)

    def open_settings_dialog(self):
        SettingsDialog(self.iface.mainWindow()).exec()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.addWidget(
            QLabel("Auto-update the dependencies at start QGIS"), 0, 0, 1, 2
        )
        self.auto_update_cb = QCheckBox(self)
        checked = QgsSettings().value("nens_dependency_loader/auto_update", True)
        self.auto_update_cb.setChecked(checked)
        layout.addWidget(self.auto_update_cb, 0, 2)

        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        layout.addItem(spacer, 1, 0)

        ok_bn = QPushButton("Ok", self)
        ok_bn.clicked.connect(self.accept)
        layout.addWidget(ok_bn, 2, 2)
        cancel_bn = QPushButton("Cancel", self)
        cancel_bn.clicked.connect(self.reject)
        layout.addWidget(cancel_bn, 2, 0)

    def accept(self):
        QgsSettings().setValue(
            "nens_dependency_loader/auto_update", self.auto_update_cb.isChecked()
        )
        super().accept()
