FROM qgis/qgis:final-3_34_4
RUN apt-get update && apt-get install -y python3-pyqt5.qtwebsockets wget python3-scipy python3-h5py zip && apt-get clean
COPY requirements-dev.txt /root
RUN pip3 install -r /root/requirements-dev.txt

# Copied the original PYTHONPATH and added the profile's python dir to imitate qgis' behaviour.
ENV PYTHONPATH=/usr/share/qgis/python/:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages/qgis:/usr/share/qgis/python/qgis:/root/.local/share/QGIS/QGIS3/profiles/default/python
# Note: we'll mount the current dir into this WORKDIR
WORKDIR /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/nens_dependency_loader
