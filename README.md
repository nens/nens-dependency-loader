# N&S Dependency Loader

QGIS comes bundled with several python libraries, but the N&S plugins need more. The required libraries are bundled with this plugin and in case a required library is missing, this plugin installs it.

## Usage

In order for your plugin to be loaded after the N&S dependency loader, append *N&S Dependency Loader* to the list of plugin dependencies in *metadata.txt*, or add the following line:

```
plugin_dependencies=N&S Dependency Loader
```

It might be the case that your plugin needs have access to the dependencies for testing (without the N&S Dependency Loader being installed). In that case, install the test dependencies in a folder in python path and generate constraints from dependency loader.

```
ADD https://raw.githubusercontent.com/nens/nens-dependency-loader/refs/heads/main/dependencies.py /root/dependencies.py
RUN python3 /root/dependencies.py
RUN pip3 install -r /root/requirements-test.txt -c /root/constraints.txt --no-deps --upgrade --target /usr/share/qgis/python/plugins
```

## Dependency handling

The extra dependencies (as wheels and tars) are retrieved and stored into the
*external-dependencies/* directory and bundled with the plugin. 

The plugin uses *dependencies.py* and installs the dependencies in the subfolder *deps/* of
the plugin folder. The dependency folder is also added (prepended) to the path. *dependencies.py* has the master list of extra dependencies.

Most are pip-installable just fine as they're pure python packages. There are some exceptions, for example *h5py*. This is a package that really needs to match various other libraries in the system. For windows, it means a custom built package (which we include in the plugin).

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
  from the *external-dependencies/* directory into the plugin's *deps/* directory. In case
  the dependency is added to the plugin as tar, the tar is extracted.

As a last step, *\_\_init__.py* calls *dependencies.check_importability* to make doubly sure all dependencies are present.

## Local development

In order to run the tests, linting and packaging, first build the docker
```
  docker-compose build
```
To run the tests:
```
  docker-compose run --rm qgis-desktop make test
```
To run the linters (flake8, black and isort):
```
  docker-compose run --rm qgis-desktop make lint
```
To create a zip:
```
   docker-compose run --rm qgis-desktop make zip
```
## Release

Make sure you have *zest.releaser* with *qgispluginreleaser* installed. The
*qgispluginreleaser* ensures the metadata.txt, which is used by the qgis plugin
manager is also updated to the new version. To make a new release enter the following
command
```
    fullrelease
```

This creates a new release and tag on github. Additionally, a zip file
*nens_dependency_loader.<version>.zip* is created. Github actions is configured to also
create this zip and upload it to https://plugins.lizard.net/ when a new tag is
created, using the *upload-artifact.sh* script.
