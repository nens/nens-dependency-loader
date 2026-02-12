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
annotated-types

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

# Download h5py 3.10.0 for QGis versions after 3.40
if ! test -f ../h5py-3.10.0.tar; then
    wget http://download.osgeo.org/osgeo4w/v2/x86_64/release/python3/python3-h5py/python3-h5py-3.10.0-1.tar.bz2
    tar -xvf python3-h5py-3.10.0-1.tar.bz2
    tar -cf h5py-3.10.0.tar -C ./apps/Python312/Lib/site-packages/ .
    cp h5py-3.10.0.tar ..
else
    echo "h5py-3.10.0.tar already present, skipping download"
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

# Download windows wheels (cp39, cp312, win, amd64)
wget https://files.pythonhosted.org/packages/2d/29/fce98fd55c7a58d0c17600f9a759ae6c3ee6851ba79ade8834ae11fe988f/threedigrid_builder-1.24.10-cp39-cp39-win_amd64.whl#sha256=6cdd4ea64b6c80dc7012d063596f9cc8ecdec05d966797a3bdcbbde968753e73
wget https://files.pythonhosted.org/packages/53/be/4bb92b7f4486633811966dd74e8b827418c0c973e84ef0adf8649fe92283/threedigrid_builder-1.24.10-cp312-cp312-win_amd64.whl#sha256=5fcfc2aa5e43c242d38f608e7d55050baa90e1155dc233a3ca9bbac5618dd5f6

wget https://files.pythonhosted.org/packages/b2/8e/83d9e3bff5c0ff7a0ec7e850c785916e616ab20d8793943f9e1d2a987fab/shapely-2.0.0-cp39-cp39-win_amd64.whl
wget https://files.pythonhosted.org/packages/7b/b3/857afd9dfbfc554f10d683ac412eac6fa260d1f4cd2967ecb655c57e831a/shapely-2.0.6-cp312-cp312-win_amd64.whl

wget https://files.pythonhosted.org/packages/b3/89/1d3b78577a6b2762cb254f6ce5faec9b7c7b23052d1cdb7237273ff37d10/greenlet-2.0.2-cp39-cp39-win_amd64.whl#sha256=db1a39669102a1d8d12b57de2bb7e2ec9066a6f2b3da35ae511ff93b01b5d564
wget https://files.pythonhosted.org/packages/43/21/a5d9df1d21514883333fc86584c07c2b49ba7c602e670b174bd73cfc9c7f/greenlet-3.1.1-cp312-cp312-win_amd64.whl#sha256=7124e16b4c55d417577c2077be379514321916d5790fa287c9ed6f23bd2ffd01

wget https://files.pythonhosted.org/packages/5f/d6/5f59a5e5570c4414d94c6da4c97731deab832cbd14eaf23189d54a92d1e1/cftime-1.6.2-cp39-cp39-win_amd64.whl#sha256=86fe550b94525c327578a90b2e13418ca5ba6c636d5efe3edec310e631757eea
wget https://files.pythonhosted.org/packages/17/98/ba5b4a2f37c6c88454b696dd5c7a4e76fc8bfd014364b47ddd7e2cec0fcd/cftime-1.6.4-cp312-cp312-win_amd64.whl#sha256=5b5ad7559a16bedadb66af8e417b6805f758acb57aa38d2730844dfc63a1e667

wget https://files.pythonhosted.org/packages/43/e4/5479fecb3606c1368d496a825d8411e126133c41224c1e7238be58b87d7e/pydantic_core-2.33.2-cp312-cp312-win_amd64.whl#sha256=f941635f2a3d96b2973e867144fde513665c87f13fe0e193c158ac51bfaaa7b2

# Download linux wheels (cp310, cp312, cp313)
wget https://files.pythonhosted.org/packages/2c/08/28d03833293a2b19073095a0cc88cd986990265ecc5b1e97a78d1ac2e817/threedigrid_builder-1.24.10-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=2135160ed5593567057791fef9cfa5dbbdd4084d5c0099f7319ff8b112fa7883
wget https://files.pythonhosted.org/packages/94/cd/4e7cda7e46c98b3fbc8c5d025e16aebfb35cfa328d7e3a3d05d8ad57a05c/threedigrid_builder-1.24.10-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=5198217c2e0ccd81d8ec0bc36f1a307d6c74095ff4b65e61344585d34e46987a
wget https://files.pythonhosted.org/packages/89/e9/ce56d73a5d651998d960e4550f8b1e6727a50bf9dc3f463e6c090fafed17/threedigrid_builder-1.24.10-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=dbb4c71f7dd8fb905f0dcad69d33433a502fd6c9033b3838ef42a68d12676e1f

wget https://files.pythonhosted.org/packages/06/07/0700e5e33c44bc87e19953244c29f73669cfb6f19868899170f9c7e34554/shapely-2.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
wget https://files.pythonhosted.org/packages/d5/7d/9a57e187cbf2fbbbdfd4044a4f9ce141c8d221f9963750d3b001f0ec080d/shapely-2.0.6-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
wget https://files.pythonhosted.org/packages/af/b0/f8169f77eac7392d41e231911e0095eb1148b4d40c50ea9e34d999c89a7e/shapely-2.0.6-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

wget https://files.pythonhosted.org/packages/6e/11/a1f1af20b6a1a8069bc75012569d030acb89fd7ef70f888b6af2f85accc6/greenlet-2.0.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=d75209eed723105f9596807495d58d10b3470fa6732dd6756595e89925ce2470
wget https://files.pythonhosted.org/packages/57/5c/7c6f50cb12be092e1dccb2599be5a942c3416dbcfb76efcf54b3f8be4d8d/greenlet-3.1.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=99cfaa2110534e2cf3ba31a7abcac9d328d1d9f1b95beede58294a60348fba36
wget https://files.pythonhosted.org/packages/d9/42/b87bc2a81e3a62c3de2b0d550bf91a86939442b7ff85abb94eec3fc0e6aa/greenlet-3.1.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=efc0f674aa41b92da8c49e0346318c6075d734994c3c4e4430b1c3f853e498e4

wget https://files.pythonhosted.org/packages/e1/17/d8042d82f44c08549b535bf2e7d1e87aa1863df5ed6cf1cf773eb2dfdf67/cftime-1.6.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=acb294fdb80e33545ae54b4421df35c4e578708a5ffce1c00408b2294e70ecef
wget https://files.pythonhosted.org/packages/04/56/233d817ef571d778281f3d639049b342f6ff0bb4de4c5ee630befbd55319/cftime-1.6.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=f92f2e405eeda47b30ab6231d8b7d136a55f21034d394f93ade322d356948654
wget https://files.pythonhosted.org/packages/c3/f8/6f13d37abb7ade46e65a08acc31af776a96dde0eb569e05d4c4b01422ba6/cftime-1.6.4.post1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=6579c5c83cdf09d73aa94c7bc34925edd93c5f2c7dd28e074f568f7e376271a0

wget https://files.pythonhosted.org/packages/31/0d/c8f7593e6bc7066289bbc366f2235701dcbebcd1ff0ef8e64f6f239fb47d/pydantic_core-2.33.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=6bdfe4b3789761f3bcb4b1ddf33355a71079858958e3a552f16d5af19768fef2
wget https://files.pythonhosted.org/packages/f9/41/4b043778cf9c4285d59742281a769eac371b9e47e35f98ad321349cc5d61/pydantic_core-2.33.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=8f57a69461af2a5fa6e6bbd7a5f60d3b7e6cebb687f55106933188e79ad155c1
wget https://files.pythonhosted.org/packages/eb/3c/f4abd740877a35abade05e437245b192f9d0ffb48bbbbd708df33d3cda37/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=9fdac5d6ffa1b5a83bca06ffe7583f5576555e6c8b3a91fbd25ea7780f825f7d

touch .generated.marker
