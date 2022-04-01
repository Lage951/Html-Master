#!/usr/bin/env python3

import torch
import sys

def Versions():
    print("VERSIONS:")
    print(f"  _sys.version                             = { sys.version}")
    print(f"  torch.__version__                        = {torch.__version__}")
    print(f"  torch.cuda.is_available()                = {torch.cuda.is_available()}")
    print(f"  torch.backends.cudnn.enabled             = {torch.backends.cudnn.enabled}")
    device = torch.device("cuda")
    print(f"  torch.cuda.get_device_properties(device) = {torch.cuda.get_device_properties(device)}")
    print(f"  torch.tensor([1.0, 2.0]).cuda()          = {torch.tensor([1.0, 2.0]).cuda()}")

def PredictDemo():
    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5m, yolov5l, yolov5x, custom

    # Images
    #img = 'https://ultralytics.com/images/zidane.jpg'  # or file, Path, PIL, OpenCV, numpy, list
    img = 'Figs/zidane.jpg'

    # Inference
    results = model(img)

    # Results
    results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
    #results.show()
    results.save('temp.jpg')
    
Versions()
PredictDemo()