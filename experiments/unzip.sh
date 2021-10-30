#!/bin/bash
cd alerceZTFv5.1
python ../unzip.py -fd light_curves_20200109.zip
cd ..

cd alerceZTFv7.1
python ../unzip.py -fd el4106_2020.zip
python ../unzip.py -fd detections_more_5_det.zip
python ../unzip.py -fd detections_with_xmatch.zip
python ../unzip.py -fd features.zip
python ../unzip.py -fd non_det_more_5.zip
python ../unzip.py -fd nondet_with_xmatch.zip
cd ..

cd PLAsTiCCv1
python ../unzip.py -fd PLAsTiCC-2018.zip
cd ..