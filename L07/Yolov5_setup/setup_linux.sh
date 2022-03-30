#!/bin/bash

set -ea

conda create --name yolov5
conda env list
conda activate yolov5

test -f yolov5 || git clone https://github.com/ultralytics/yolov5 
cd yolov5
pip install -r requirements.txt 