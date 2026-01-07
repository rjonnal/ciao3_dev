#!/usr/bin/bash
rm centroid.c
rm ../centroid.so
rm *.so
python setup.py build_ext --inplace
rm -rfv build
#python test_cython_only.py
cp centroid.cpython*.so ../centroid.so
