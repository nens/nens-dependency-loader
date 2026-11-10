#!/bin/bash
export LANG=C.UTF-8

# Fail immediately upon error exit code.
set -e

# Cleanup, we don't want old stuff to linger around.
rm -f *.whl
rm -rf *.egg
rm -f *.gz
rm -rf SQLAlchemy*
rm -rf build

# Download pure python dependencies and convert them to wheels.
pip3 wheel --constraint ../constraints.txt --no-deps \
GeoAlchemy2 \
alembic \
cached-property \
click \
colorama \
condenser \
h5netcdf \
importlib-resources \
mako \
networkx \
packaging \
pyqtgraph \
python-editor \
threedi-mi-utils \
threedi-modelchecker \
threedi-schema \
threedidepth \
threedigrid \
typing-extensions \
zipp \
hydxlib \
threedi-api-client \
six \
urllib3 \
requests \
python-dateutil \
PyJWT \
certifi \
threedi-scenario-downloader \
bridgestyle \
pydantic \
typing-inspection \
annotated-types \
mistune

# Start a build/ directory for easier later cleanup.
mkdir build
cd build

# Due to a very slow server the following dependencies are not downloaded if already present
# Download the custom compiled qgis version tar of h5py, create a tar from the distro subfolder
# Download h5py 3.8.0 for QGis versions before 3.40
if ! test -f ../h5py-3.8.0.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-h5py/python3-h5py-3.8.0-1.tar.bz2
    tar -xvf python3-h5py-3.8.0-1.tar.bz2
    tar -cf h5py-3.8.0.tar -C ./apps/Python39/Lib/site-packages/ .
    cp h5py-3.8.0.tar ..
else
    echo "h5py-3.8.0.tar already present, skipping download"
fi

# Download h5py 3.10.0 for QGis versions 3.40 - 4.2
if ! test -f ../h5py-3.10.0.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-h5py/python3-h5py-3.10.0-1.tar.bz2
    tar -xvf python3-h5py-3.10.0-1.tar.bz2
    tar -cf h5py-3.10.0.tar -C ./apps/Python312/Lib/site-packages/ .
    cp h5py-3.10.0.tar ..
else
    echo "h5py-3.10.0.tar already present, skipping download"
fi

# Download h5py 3.16.0 for QGis versions after 4.2 (numpy 2.x compatible)
if ! test -f ../h5py-3.16.0.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-h5py/python3-h5py-3.16.0-1.tar.bz2
    tar -xvf python3-h5py-3.16.0-1.tar.bz2
    tar -cf h5py-3.16.0.tar -C ./apps/Python312/Lib/site-packages/ .
    cp h5py-3.16.0.tar ..
else
    echo "h5py-3.16.0.tar already present, skipping download"
fi

# as well as scipy
# Download scipy 1.10.1 for QGis versions before 3.40
if ! test -f ../scipy-1.10.1.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-scipy/python3-scipy-1.10.1-1.tar.bz2
    tar -xvf python3-scipy-1.10.1-1.tar.bz2
    tar -cf scipy-1.10.1.tar -C ./apps/Python39/Lib/site-packages/ .
    cp scipy-1.10.1.tar ..
else
    echo "scipy-1.10.1.tar already present, skipping download"
fi

# Download scipy 1.13.0 for QGis versions after 3.40
if ! test -f ../scipy-1.13.0.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-scipy/python3-scipy-1.13.0-1.tar.bz2
    tar -xvf python3-scipy-1.13.0-1.tar.bz2
    tar -cf scipy-1.13.0.tar -C ./apps/Python312/Lib/site-packages/ .
    cp scipy-1.13.0.tar ..
else
    echo "scipy-1.13.0.tar already present, skipping download"
fi

# Back up a level and clean up the build/ directory.
cd ..
rm -rf build

# Copy the compiled windows scipy to external dependencies
cp scipy/scipy-1.6.2-cp39-cp39-win_amd64.whl .

# Also copy the custom compiled windows h5py to external dependencies for QGis versions before 3.28.6
cp h5py/h5py-2.10.0-cp39-cp39-win_amd64.whl .

# Copy pure wheels to prevent pip in docker (or Windows) to select platform dependent version
wget https://files.pythonhosted.org/packages/b8/d9/13bdde6521f322861fab67473cec4b1cc8999f3871953531cf61945fad92/sqlalchemy-2.0.43-py3-none-any.whl#sha256=1681c21dd2ccee222c2fe0bef671d1aef7c504087c9c4e800371cfcc8ac966fc

# Download windows wheels (cp312, cp314)
wget https://files.pythonhosted.org/packages/53/be/4bb92b7f4486633811966dd74e8b827418c0c973e84ef0adf8649fe92283/threedigrid_builder-1.24.10-cp312-cp312-win_amd64.whl#sha256=5fcfc2aa5e43c242d38f608e7d55050baa90e1155dc233a3ca9bbac5618dd5f6
wget https://files.pythonhosted.org/packages/28/1c/adbdffa05271fe66bd041f29df81868ea0e01f35bf6eb39b259b8d9e218e/threedigrid_builder-1.25.3-cp312-cp312-win_amd64.whl#sha256=c1aefe3ea0692ed46df1bd63847a8998c640d1e86b598dcfd2349a11f83f964b
wget https://files.pythonhosted.org/packages/7b/b3/857afd9dfbfc554f10d683ac412eac6fa260d1f4cd2967ecb655c57e831a/shapely-2.0.6-cp312-cp312-win_amd64.whl
wget https://files.pythonhosted.org/packages/43/21/a5d9df1d21514883333fc86584c07c2b49ba7c602e670b174bd73cfc9c7f/greenlet-3.1.1-cp312-cp312-win_amd64.whl#sha256=7124e16b4c55d417577c2077be379514321916d5790fa287c9ed6f23bd2ffd01
wget https://files.pythonhosted.org/packages/17/98/ba5b4a2f37c6c88454b696dd5c7a4e76fc8bfd014364b47ddd7e2cec0fcd/cftime-1.6.4-cp312-cp312-win_amd64.whl#sha256=5b5ad7559a16bedadb66af8e417b6805f758acb57aa38d2730844dfc63a1e667
wget https://files.pythonhosted.org/packages/20/dd/12f4c03bc6e065d4243f5dffb61e2d73a39663ce27a2da1ac68746459308/pydantic_core-2.35.2-cp312-cp312-win_amd64.whl#sha256=6544065eb63995e6c8f30119c8297acab0426c7231f33b792fb6176c29ba771

# Download linux wheels (cp312, cp313, cp314)
wget https://files.pythonhosted.org/packages/94/cd/4e7cda7e46c98b3fbc8c5d025e16aebfb35cfa328d7e3a3d05d8ad57a05c/threedigrid_builder-1.24.10-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=5198217c2e0ccd81d8ec0bc36f1a307d6c74095ff4b65e61344585d34e46987a
wget https://files.pythonhosted.org/packages/89/e9/ce56d73a5d651998d960e4550f8b1e6727a50bf9dc3f463e6c090fafed17/threedigrid_builder-1.24.10-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=dbb4c71f7dd8fb905f0dcad69d33433a502fd6c9033b3838ef42a68d12676e1f
wget https://files.pythonhosted.org/packages/38/7b/ec37e8c315c0414ecf72bc5cc5464368477bddb61fd5edd3370312560677/threedigrid_builder-1.25.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=748272883c72eeec92b88e91b4229371f43da17e714fdae176740c7befd3e2c4
wget https://files.pythonhosted.org/packages/ad/21/55125aedfcb5cda6b95e2b2e779df80abe757470a863815bfbbc9ddbf5d2/threedigrid_builder-1.25.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=9143589f2301bd64769f7d55b3b52a8a238aeef89fae37c523c2896074a34332
wget https://files.pythonhosted.org/packages/89/12/f5f88145d0986a9756a0875cdf6bf59054c9af0eacc3a51007df84a52220/threedigrid_builder-1.25.8-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl#sha256=1738715a4deaa15ec998e5d82782603ea179bc7c12f71daed7730abc72ed2a43

wget https://files.pythonhosted.org/packages/d5/7d/9a57e187cbf2fbbbdfd4044a4f9ce141c8d221f9963750d3b001f0ec080d/shapely-2.0.6-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
wget https://files.pythonhosted.org/packages/af/b0/f8169f77eac7392d41e231911e0095eb1148b4d40c50ea9e34d999c89a7e/shapely-2.0.6-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
wget https://files.pythonhosted.org/packages/8a/cb/4948be52ee1da6927831ab59e10d4c29baa2a714f599f1f0d1bc747f5777/shapely-2.1.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl#sha256=21952dc00df38a2c28375659b07a3979d22641aeb104751e769c3ee825aadecf

wget https://files.pythonhosted.org/packages/57/5c/7c6f50cb12be092e1dccb2599be5a942c3416dbcfb76efcf54b3f8be4d8d/greenlet-3.1.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=99cfaa2110534e2cf3ba31a7abcac9d328d1d9f1b95beede58294a60348fba36
wget https://files.pythonhosted.org/packages/d9/42/b87bc2a81e3a62c3de2b0d550bf91a86939442b7ff85abb94eec3fc0e6aa/greenlet-3.1.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=efc0f674aa41b92da8c49e0346318c6075d734994c3c4e4430b1c3f853e498e4
wget https://files.pythonhosted.org/packages/f7/38/f958ee90fab93529b30cc1e4a59b27c1112b640570043a84af84da3b3b98/greenlet-3.2.5-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl#sha256=6712bfd520530eb67331813f7112d3ee18e206f48b3d026d8a96cd2d2ad20251

wget https://files.pythonhosted.org/packages/04/56/233d817ef571d778281f3d639049b342f6ff0bb4de4c5ee630befbd55319/cftime-1.6.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=f92f2e405eeda47b30ab6231d8b7d136a55f21034d394f93ade322d356948654
wget https://files.pythonhosted.org/packages/c3/f8/6f13d37abb7ade46e65a08acc31af776a96dde0eb569e05d4c4b01422ba6/cftime-1.6.4.post1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=6579c5c83cdf09d73aa94c7bc34925edd93c5f2c7dd28e074f568f7e376271a0
wget https://files.pythonhosted.org/packages/b4/aa/e2e5c07f57233d171a0506153d2f50dc3d09e9f6273b2a578f76379d1526/cftime-1.6.6-cp311-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl#sha256=59a2c7821642b62c18e71ea67f84ce13ec2bb51ce7ee348cf0a3c50d55fd91cb

wget https://files.pythonhosted.org/packages/cc/de/560965eb01915181a0f966c2b567dcb43c70114a7115197f2ef6d9aab9ee/pydantic_core-2.35.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=85014d39aeffc3eef49ca31dcfae7e33deb318d98bc91d3641c5237452e9fc2
wget https://files.pythonhosted.org/packages/31/13/cb780bc228619f3b2e5e9395a9efad5030fb3fbe658e25856ba270fc0bbd/pydantic_core-2.35.2-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=70bc9c0984b9b6da0f064cd5a1b6b5111637f30dd05999f565faa6d5e10e5e62

touch .generated.marker
