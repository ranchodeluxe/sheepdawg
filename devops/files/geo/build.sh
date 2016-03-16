#!/bin/bash
GEOS_TAR=http://download.osgeo.org/geos/geos-3.5.0.tar.bz2
PROJ4_TAR=https://github.com/OSGeo/proj.4/archive/4.9.2.tar.gz
GDAL_TAR=http://download.osgeo.org/gdal/1.11.3/gdal-1.11.3.tar.gz
PREFIX_DIR=~/lambda/local
GEOS_CONFIG=$PREFIX_DIR/bin/geos-config
GDAL_CONFIG=$PREFIX_DIR/bin/gdal-config

#
# create working dir
#
# ~/lambda/
#   lambda_handler.py
#   lambda_worker.py
#   virtualenvs/
#     local/
#       lib/
#         *.so 
#
mkdir -p ~/lambda/local
cd lambda

#
# binary package deps
#
sudo yum install python27-devel python27-pip gcc libjpeg-devel zlib-devel gcc-c++

#
# create virtualenv 
# we have to do this before 
# GDAL python plugin is installed
#
virtualenv --python=/usr/bin/python ~/lambda/venv
source ~/lambda/venv/bin/activate

#
# unpack and build
#
tarfile=$(basename $PROJ4_TAR);
#file_ext=$(echo $tarfile | awk '{print $NF}' FS='[[:digit:]].')
#extracted_name=$(echo $tarfile | awk '{print $NR}' FS=.$file_ext)
wget $PROJ4_TAR
tar -xzvf $tarfile
cd proj.4-4.9.2/
./configure --prefix=$PREFIX_DIR
make &> PROJ4_MAKE.out
make install &> PROJ4_MAKEINSTALL.out
cd ../

tarfile=$(basename $GEOS_TAR);
wget $GEOS_TAR
tar -xjvf $tarfile
cd geos-3.5.0/
./configure --prefix=$PREFIX_DIR
make &> GEOS_MAKE.out
make install &> GEOS_MAKEINSTALL.out
cd ../

tarfile=$(basename $GDAL_TAR);
wget $GDAL_TAR
tar -xzvf $tarfile
cd gdal-1.11.3/
./configure --prefix=$PREFIX_DIR \
            --with-geos=$GEOS_CONFIG \
            --with-python \
            --with-static-proj4=$PREFIX_DIR
make &> GDAL_MAKE.out
make install &> GDAL_MAKEINSTALL.out
cd ../

#
# export required ENVS for raterio, shapely and fiona
#
export GEOS_CONFIG=$GEOS_CONFIG
export GDAL_CONFIG=$GDAL_CONFIG

#
# pip install requirements
#
pip install numpy==1.10.4
pip install rasterio==0.31.0
pip install Fiona==1.6.3
pip install Shapely==1.5.13
