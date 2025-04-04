from nens_dependency_loader import dependencies
from qgis.core import QgsApplication

import logging
import pytest


logger = logging.getLogger(__name__)
_singletons = {}


@pytest.fixture(autouse=True)
def qgis_app_initialized():
    """Make sure qgis is initialized for testing."""
    if "app" not in _singletons:
        app = QgsApplication([], False)
        app.initQgis()
        logger.debug("Initialized qgis (for testing). Settings: %s", app.showSettings())
        _singletons["app"] = app

    dependencies.ensure_everything_installed()
