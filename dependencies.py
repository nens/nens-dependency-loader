from collections import namedtuple
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QMessageBox

import importlib
import logging
import os
import pkg_resources
import platform
import setuptools  # noqa: https://github.com/pypa/setuptools/issues/2993
import shutil
import subprocess
import sys
import tarfile


# If you add a dependency, also adjust external-dependencies/populate.sh. in case
# the dependency is a tar, the constraint should be the explicit version(e.g. "==3.8.0")
Dependency = namedtuple("Dependency", ["name", "package", "constraint", "tar"])

DEPENDENCIES = [
    Dependency("SQLAlchemy", "sqlalchemy", "==2.0.6", False),
    Dependency("GeoAlchemy2", "geoalchemy2", "==0.15.*", False),
    Dependency("pyqtgraph", "pyqtgraph", ">=0.13.2", False),
    Dependency(
        "importlib-resources", "importlib_resources", "", False
    ),  # backward compat. alembic
    Dependency("zipp", "zipp", "", False),  # backward compat. alembic
    Dependency("Mako", "mako", "", False),
    Dependency("cftime", "cftime", ">=1.5.0", False),  # threedigrid[results]
    Dependency("alembic", "alembic", "==1.14.*", False),
    Dependency("threedigrid", "threedigrid", "==2.3.*", False),
    Dependency("threedi-schema", "threedi_schema", "==0.300.26", False),
    Dependency("threedi-modelchecker", "threedi_modelchecker", "==2.18.1", False),
    Dependency("threedidepth", "threedidepth", "==0.6.3", False),
    Dependency("click", "click", ">=8.0", False),
    Dependency("packaging", "packaging", "", False),
    Dependency("typing-extensions", "typing_extensions", ">=4.2.0", False),
    Dependency(
        "colorama", "colorama", "", False
    ),  # dep of click and threedi-modelchecker (windows)
    Dependency("networkx", "networkx", "", False),
    Dependency("condenser", "condenser", ">=0.2.1", False),
    Dependency("Shapely", "shapely", ">=2.0.0", False),
    Dependency("threedigrid-builder", "threedigrid_builder", ">=1.24.3", False),
    Dependency("h5netcdf", "h5netcdf", "", False),
    Dependency("greenlet", "greenlet", "!=0.4.17", False),
    Dependency("threedi-mi-utils", "threedi_mi_utils", "==0.1.10", False),
    Dependency("hydxlib", "hydxlib", "==1.7.3", False),
    Dependency("threedi-api-client", "threedi_api_client", "==4.1.11.dev0", False),
    Dependency("six", "six", "", False),
    Dependency("urllib3", "urllib3", "", False),
    Dependency("requests", "requests", "", False),
    Dependency("python-dateutil", "dateutil", "", False),
    Dependency("PyJWT", "jwt", "", False),
    Dependency("certifi", "certifi", "", False),
    Dependency("threedi-scenario-downloader", "threedi_scenario_downloader", "", False),
]

# On Windows, the hdf5 binary and thus h5py version depends on the QGis version
# QGis upgraded from hdf5 == 1.10.7 to hdf5 == 1.14.0 in QGis 3.28.6
QGIS_VERSION = Qgis.QGIS_VERSION_INT
if QGIS_VERSION < 32806 and platform.system() == "Windows":
    H5PY_DEPENDENCY = Dependency("h5py", "h5py", "==2.10.0", False)
elif QGIS_VERSION >= 34000 and platform.system() == "Windows":
    H5PY_DEPENDENCY = Dependency("h5py", "h5py", "==3.10.0", True)
else:
    H5PY_DEPENDENCY = Dependency("h5py", "h5py", "==3.8.0", True)

if QGIS_VERSION < 32811 and platform.system() == "Windows":
    WINDOWS_PLATFORM_DEPENDENCIES = [
        Dependency("scipy", "scipy", "==1.6.2", False),
    ]
elif QGIS_VERSION >= 34000 and platform.system() == "Windows":
    WINDOWS_PLATFORM_DEPENDENCIES = [
        Dependency("scipy", "scipy", "==1.13.0", True),
    ]
else:
    WINDOWS_PLATFORM_DEPENDENCIES = [
        Dependency("scipy", "scipy", "==1.10.1", True),
    ]

INTERESTING_IMPORTS = ["numpy", "osgeo", "pip", "setuptools"]

OUR_DIR = Path(__file__).parent

logger = logging.getLogger(__name__)


def create_progress_dialog(progress, text):
    dialog = QProgressDialog()
    dialog.setWindowTitle("N&S Dependency Loader install progress")
    dialog.setLabelText(text)
    dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
    bar = QProgressBar(dialog)
    bar.setTextVisible(True)
    bar.setValue(progress)
    bar.setValue(0)
    bar.setMaximum(100)
    dialog.setBar(bar)
    dialog.setMinimumWidth(500)
    dialog.update()
    dialog.setCancelButton(None)
    dialog.show()
    return dialog, bar


def ensure_everything_installed():
    """Check if DEPENDENCIES are installed and install them if missing."""

    # If required, create deps folder and prepend to the path
    target_dir = _dependencies_target_dir(create=True)
    if str(target_dir) not in sys.path:
        sys.path.insert(0, str(target_dir))

    _refresh_python_import_mechanism()

    _ensure_prerequisite_is_installed()

    missing = _check_presence(DEPENDENCIES)
    restart_required = False
    if platform.system() == "Windows":
        missing += _check_presence(WINDOWS_PLATFORM_DEPENDENCIES)
        if not _ensure_h5py_installed(target_dir):
            restart_required = True

    if missing:
        print("Missing dependencies:")
        for deps in missing:
            print(deps.name)

        try:
            _install_dependencies(missing, target_dir=target_dir)
        except RuntimeError:
            # In case some libraries are already imported, we cannot uninstall
            # because QGIS acquires a lock on dll/pyd-files. Therefore
            # we need to restart Qgis.
            restart_required = True
            pass

        restart_marker = Path(target_dir / "restarted.marker")

        if restart_required or not restart_marker.exists():
            if _is_windows():
                # We always want to restart when deps are missing
                msg = "Please restart QGIS to complete the installation "
                msg += "process of Nelen & Schuurmans Dependency Loader."
                QMessageBox.information(
                    None,
                    "Restart required",
                    msg,
                )

                restart_marker.touch()

        # Always update the import mechanism
        _refresh_python_import_mechanism()

    else:
        print("Dependencies up to date")


def _ensure_h5py_installed(target_dir):
    """
    On Windows Qgis comes with a hdf5 version installed.
    This plugin uses the h5py python package, which is built against a specific version
    of HDF5. The Qgis HDF5 version and the HDF5 version of the h5py package must be the
    same, otherwise it will not work. In the external-dependencies folder we supply a
    Windows version of h5py.

    In version 3.28.6, QGis updated their HDF5.dll binary from 1.10.7 to 1.14.0.
    """

    h5py_missing = _check_presence([H5PY_DEPENDENCY])

    if not h5py_missing:
        # Sometimes DLL remain after a reinstall of the plugin, this incorrectly makes
        # pkg_resources think that h5py is still present. Do explicit check on file
        # to make sure.
        h5py_version_file = target_dir / H5PY_DEPENDENCY.name / "version.py"
        if not h5py_version_file.exists():
            # clean the remnants and mark as missing
            _uninstall_dependency(H5PY_DEPENDENCY)
            h5py_missing = True

    if h5py_missing:
        try:
            _install_dependencies(
                [H5PY_DEPENDENCY], target_dir=_dependencies_target_dir()
            )
        except PermissionError:
            return False

    return True


def _ensure_prerequisite_is_installed(prerequisite="pip"):
    """Check the basics: pip.

    People using OSGEO custom installs sometimes exclude those
    dependencies. Our installation scripts fail, then, because of the missing
    'pip'.

    """
    try:
        importlib.import_module(prerequisite)
    except Exception as e:
        msg = (
            "%s. 'pip', which we need, is missing. It is normally included with "
            "python. You are *probably* using a custom minimal OSGEO release. "
            "Please re-install with 'pip' included."
        ) % e
        print(msg)
        raise RuntimeError(msg)


def _dependencies_target_dir(our_dir=OUR_DIR, create=False) -> Path:
    """Return (and create) the desired deps folder

    This is the 'deps' subdirectory of the plugin home folder

    """
    target_dir = our_dir / "deps"
    if not target_dir.exists() and create:
        target_dir.mkdir()

    return target_dir


def check_importability():
    """Check if the dependendies are importable and log the locations.

    If something is not importable, which should not happen, it raises an
    ImportError automatically. Which is exactly what we want, because we
    cannot continue.

    """
    packages = [dependency.package for dependency in DEPENDENCIES]
    packages += INTERESTING_IMPORTS
    logger.info("sys.path:\n    %s", "\n    ".join(sys.path))
    deps_in_target_dir = [item.name for item in _dependencies_target_dir().iterdir()]
    logger.info(
        "Contents of our dependency dir:\n    %s",
        "\n    ".join(deps_in_target_dir),
    )
    for package in packages:
        imported_package = importlib.import_module(package)
        logger.info(
            "Import '%s' found at \n    '%s'", package, imported_package.__file__
        )


def _uninstall_dependency(dependency):
    print("Trying to uninstalling dependency %s" % dependency.name)
    if dependency.tar:
        # just remove the folders
        path = _dependencies_target_dir()
        items_to_remove = [
            node
            for node in os.listdir(str(path))
            if (dependency.package in node or dependency.name in node)
        ]
        for f in items_to_remove:
            dep_path = str(path / f)

            try:
                if os.path.exists(dep_path):
                    if os.path.isfile(dep_path):
                        print(f"Deleting file {f} from {path}")
                        os.remove(dep_path)
                    else:
                        print(f"Deleting folder {f} from {path}")
                        shutil.rmtree(dep_path)
            except Exception as e:
                print(f"Unable to remove {dep_path} ({str(e)})")
        return

    python_interpreter = _get_python_interpreter()
    startupinfo = None
    if _is_windows():
        startupinfo = subprocess.STARTUPINFO()
        # Prevents terminal screens from popping up
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        process = subprocess.Popen(
            [
                python_interpreter,
                "-m",
                "pip",
                "uninstall",
                "--yes",
                (dependency.name),
            ],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
        )
        # The input/output/error stream handling is a bit involved, but it is
        # necessary because of a python bug on windows 7, see
        # https://bugs.python.org/issue3905 .
        i, o, e = (process.stdin, process.stdout, process.stderr)
        i.close()
        result = o.read() + e.read()
        o.close()
        e.close()
        print(result)
        exit_code = process.wait()
        if exit_code:
            print("Uninstalling %s failed" % dependency.name)
    except Exception:
        print("Uninstalling %s failed" % dependency.name)


def _install_dependencies(dependencies, target_dir):
    if not dependencies:
        return

    python_interpreter = _get_python_interpreter()
    base_command = [
        python_interpreter,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--no-deps",
        "--find-links",
        str(OUR_DIR / "external-dependencies"),
        "--no-index",
        "--target",
        str(target_dir),
    ]

    dialog = None
    bar = None
    startupinfo = None
    if _is_windows():
        dialog, bar = create_progress_dialog(0, f"Installing {dependencies[0].name}")
        QApplication.processEvents()
        startupinfo = subprocess.STARTUPINFO()
        # Prevents terminal screens from popping up
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    for count, dependency in enumerate(dependencies):
        _uninstall_dependency(dependency)
        print("Installing '%s' into %s" % (dependency.name, target_dir))
        if dialog:
            dialog.setLabelText(f"Installing {dependency.name}")

        if dependency.tar:
            # Just extract the tar into the target folder, we already now it exists
            tar_path = f"{(OUR_DIR / 'external-dependencies')}/{dependency.name}"
            tar_path += f"-{dependency.constraint[2:]}.tar"
            tar = tarfile.open(tar_path)
            tar.extractall(str(target_dir))
            tar.close()
        else:
            command = base_command + [dependency.name + dependency.constraint]

            process = subprocess.Popen(
                command,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
            )
            # The input/output/error stream handling is a bit involved, but it is
            # necessary because of a python bug on windows 7, see
            # https://bugs.python.org/issue3905 .
            i, o, e = (process.stdin, process.stdout, process.stderr)
            i.close()
            result = o.read() + e.read()
            o.close()
            e.close()
            print(result)
            exit_code = process.wait()
            if exit_code:
                if dialog:
                    dialog.close()
                    QApplication.processEvents()
                raise RuntimeError(
                    f"Installing {dependency.name} failed ({exit_code}) ({result})"
                )

        print("Installed %s into %s" % (dependency.name, target_dir))
        if dependency.package in sys.modules:
            print("Unloading old %s module" % dependency.package)
            del sys.modules[dependency.package]
            # check_importability() will be called soon, which will import them again.
            # By removing them from sys.modules, we prevent older versions from
            # sticking around.

        if bar:
            bar.setValue(int((count / len(dependencies)) * 100))
            bar.update()
            QApplication.processEvents()

    if dialog:
        dialog.close()


def _is_windows():
    """Return whether we are starting from QGIS on Windows."""
    executable = sys.executable
    _, filename = os.path.split(executable)
    if "python3" in filename.lower():
        return False
    elif "qgis" in filename.lower():
        if platform.system().lower() == "darwin":
            return False
        else:
            return True
    else:
        raise EnvironmentError("Unexpected value for sys.executable: %s" % executable)


def _get_python_interpreter():
    """Return the path to the python3 interpreter.

    Under linux sys.executable is set to the python3 interpreter used by Qgis.
    However, under Windows/Mac this is not the case and sys.executable refers to the
    Qgis start-up script.
    """
    interpreter = None
    executable = sys.executable
    directory, _ = os.path.split(executable)
    if _is_windows():
        interpreter = os.path.join(directory, "python3.exe")
    elif platform.system().lower() == "darwin":
        interpreter = os.path.join(directory, "bin", "python3")
    else:
        interpreter = executable

    assert os.path.exists(interpreter)  # safety check
    return interpreter


def _check_presence(dependencies):
    """Check if all dependencies are present. Return missing dependencies."""
    missing = []
    for dependency in dependencies:
        requirement = dependency.name + dependency.constraint
        print("Checking presence of %s..." % requirement)
        try:
            result = pkg_resources.require(requirement)
            print("Requirement %s found: %s" % (requirement, result))
        except pkg_resources.DistributionNotFound as e:
            print(
                "Dependency '%s' (%s) not found (%s)"
                % (dependency.name, dependency.constraint, str(e))
            )
            missing.append(dependency)
        except pkg_resources.VersionConflict as e:
            print(
                "Version conflict:\n"
                f"    Installed: {e.dist}\n"
                f"    Required: {e.req}"
            )
            if isinstance(e, pkg_resources.ContextualVersionConflict):
                print(f"    By: {e.required_by}")
            missing.append(dependency)
        except Exception as e:
            print(
                "Installing dependency '%s' (%s) went wrong (%s)"
                % (dependency.name, dependency.constraint, str(e))
            )
            missing.append(dependency)
    return missing


def _refresh_python_import_mechanism():
    """Refresh the import mechanism.

    This is required when deps are dynamically installed/removed. The modules
    'importlib' and 'pkg_resources' need to update their internal data structures.
    """
    # This function should be called if any modules are created/installed while your
    # program is running to guarantee all finders will notice the new module’s
    # existence.
    importlib.invalidate_caches()

    # https://stackoverflow.com/questions/58612272/pkg-resources-get-distributionmymodule-version-not-updated-after-reload
    # Apparantely pkg_resources needs to be reloaded to be up-to-date with newly
    # installed packages
    importlib.reload(pkg_resources)


def generate_constraints_txt(target_dir=OUR_DIR):
    """Called from the ``__main__`` to generate ``constraints.txt``."""
    constraints_file = target_dir / "constraints.txt"
    lines = ["# Generated by dependencies.py"]
    lines += [(dependency.name + dependency.constraint) for dependency in DEPENDENCIES]
    lines.append("")
    constraints_file.write_text("\n".join(lines))
    print("Wrote constraints to %s" % constraints_file)


if __name__ == "__main__":  # pragma: no cover
    generate_constraints_txt()
