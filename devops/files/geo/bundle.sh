#!/bin/bash
cd ~/lambda
source venv/bin/activate

#
# virtualenvs
#
PYSITE_PKG1=$VIRTUAL_ENV/lib64/python2.7/site-packages
cd PYSITE_PKG1
zip -r9 ~/lambda/bundle.zip *
PYSITE_PKG2=$VIRTUAL_ENV/lib/python2.7/site-packages
cd PYSITE_PKG2
zip -r9 ~/lambda/bundle.zip *

#
# shared libs
#
for fhandle in  ~/lambda/local/lib/libgdal.so \
                ~/lambda/local/lib/libgdal.so.1 \
                ~/lambda/local/lib/libgeos_c.so \
                ~/lambda/local/lib/libgeos_c.so.1
do
  if [ -f $fhandle ] ; then
    zip -r9 ~/lambda/bundle.zip $fhandle;
  fi
done
