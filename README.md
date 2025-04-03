# N&S Dependency Loader

Qgis comes bundled with several python libraries, but we need a few more. The
extra dependencies (as wheels and tars) are retrieved and stored into the
*external-dependencies/* directory and bundled with the plugin.

The plugin uses *dependencies.py* and installs the dependencies in the subfolder *deps/* of
the plugin folder. The dependency folder is also added (prepended) to the path.

*dependencies.py* has the master list of extra dependencies.

Most are pip-installable just fine as they're pure python packages. There are some exceptions, for example *h5py*. This is a package that really needs to match various other libraries in the system. For windows, it means a custom built package (which we include in the plugin).

## Our dependency handling


*dependencies.py* can be called directly, which generates a *constraints.txt* file for use with pip. The *Makefile* handles this for us: it updates the constraints file.

The *external-dependencies/* directory has a *populate.sh* script. The *Makefile* runs it when needed. It populates the directory with our dependencies so that we can bundle it with the plugin:

- *populate.sh* uses *pip3 wheel* to create universal wheel files for the
  four pure python libaries.
- It also downloads and tars the custom build of *h5py* from QGIS.

The *ensure_everything_installed* function is called by our main *\_\_init__.py*:

- It first checks if the correct versions of our dependencies are
  installed. It doesn't matter where they're installed: system packages,
  qgis-bundled or in the profile directory.
- If something is missing, it calls python3's build-in "pip" to install it
  from the *external-dependencies/* directory into the plugin's *deps/* directory.

As a last step, *\_\_init__.py* calls *dependencies.check_importability* to make doubly sure all dependencies are present.
