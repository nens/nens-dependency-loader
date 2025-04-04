from nens_dependency_loader.nens_dependency_loader import NenSDependencyLoader
from pathlib import Path

import configparser
import mock


PLUGIN_DIR = Path(__file__).parent.parent


def test_read_init():
    """Test that the plugin __init__ will validate on plugins.qgis.org."""

    # You should update this list according to the latest in
    # https://github.com/qgis/qgis-django/blob/master/qgis-app/plugins/validator.py
    required_metadata = [
        "name",
        "description",
        "version",
        "qgisMinimumVersion",
        "email",
        "author",
        "about",
        "tracker",
        "repository",
    ]

    metadata_file = PLUGIN_DIR / "metadata.txt"
    metadata = []
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(metadata_file, encoding="utf-8")
    message = 'Cannot find a section named "general" in %s' % metadata_file
    assert parser.has_section("general"), message
    metadata.extend(parser.items("general"))

    for key in required_metadata:
        message = 'Cannot find mandatory metadata "%s" in metadata source (%s).' % (
            key,
            metadata_file,
        )
        assert key in dict(metadata), message


def test_smoke():
    NenSDependencyLoader(mock.Mock())
