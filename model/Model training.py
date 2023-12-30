# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rYzUgB2do-S3o9PxzBRdmtksh4fH5x2y
"""

!python -m pip install pyyaml==5.1
!python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

!pip install labelme
!pip install labelme2coco
!pip install rarfile

from google.colab import drive
drive.mount('/content/drive')

from rarfile import RarFile
import os

rar_file_path = '/content/drive/MyDrive/face_project.rar'
extracted_path = '/content/'

os.makedirs(extracted_path, exist_ok=True)

with RarFile(rar_file_path, 'r') as rar:
    rar.extractall(extracted_path)


extracted_contents = os.listdir(extracted_path)
extracted_contents



import torch
import detectron2
!nvcc --version
TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
print("detectron2:", detectron2.__version__)

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

import numpy as np
import cv2
import matplotlib.pyplot as plt

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

# Set GPU memory limit
torch.cuda.set_per_process_memory_fraction(0.5)

classes = ['Mask', 'No Mask']

from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.data.datasets import register_coco_instances



# DatasetCatalog.register('mask_dataset', lambda: get_mask_dicts('PATH/TO/MAIN_DIR_WITH_IMAGES_ANNOTATIONS'))
# MetadataCatalog.get('mask_dataset').set(thing_classes=classes)

# Train dataset
register_coco_instances("train_dataset", {}, "/content/train.json", "/content/train_images")
MetadataCatalog.get("train_dataset").set(thing_classes=classes)
train_metadata = MetadataCatalog.get('train_dataset')

# Test dataset
register_coco_instances("test_dataset", {}, "/content/test.json", "/content/test_images")
MetadataCatalog.get("test_dataset").set(thing_classes=classes)
test_metadata = MetadataCatalog.get('test_dataset')

# Validation dataset
register_coco_instances("valid_dataset", {}, "/content/valid.json", "/content/valid_images")
MetadataCatalog.get("valid_dataset").set(thing_classes=classes)
valid_metadata = MetadataCatalog.get('valid_dataset')

import random
from detectron2.utils.visualizer import Visualizer

dataset_dicts = DatasetCatalog.get('train_dataset')
for d in random.sample(dataset_dicts, 5):
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=train_metadata)
    vis = visualizer.draw_dataset_dict(d)
    plt.figure(figsize = (14, 10))
    plt.imshow(cv2.cvtColor(vis.get_image()[:, :, ::-1], cv2.COLOR_BGR2RGB))
    plt.show()

# from detectron2.engine import DefaultTrainer
# from detectron2.config import get_cfg

# cfg = get_cfg()
# # cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
# #cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_C4_3x.yaml"))
# #cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))

# cfg.DATASETS.TRAIN = ('train_dataset',)
# cfg.DATASETS.TEST = ()   # no metrics implemented for this dataset
# cfg.DATALOADER.NUM_WORKERS = 2
# # cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
# #cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_C4_3x.yaml")
# #cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")

# cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(classes)

# # cfg.SOLVER.IMS_PER_BATCH = 4
# # cfg.SOLVER.BASE_LR = 0.001
# # cfg.SOLVER.WARMUP_ITERS = 1000
# # cfg.SOLVER.MAX_ITER = 1000
# cfg.SOLVER.STEPS = [] # do not decay learning rate
# #cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512 **
# # cfg.SOLVER.GAMMA = 0.05

# # cfg = get_cfg()
# cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_C4_3x.yaml"))
# cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_C4_3x.yaml")
# cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6
# # cfg.DATASETS.TRAIN = ("train_dataset",)
# # cfg.DATASETS.TEST = ("test_dataset",)

# cfg.SOLVER.MAX_ITER = 1000
# cfg.SOLVER.BASE_LR = 0.001
# cfg.SOLVER.IMS_PER_BATCH = 2  # Adjust this value based on available GPU memory

# os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
# trainer = DefaultTrainer(cfg)
# trainer.resume_or_load(resume=False)
# trainer.train()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6
cfg.DATASETS.TRAIN = ("train_dataset",)
cfg.DATASETS.TEST = ("test_dataset",)

cfg.SOLVER.MAX_ITER = 1000
cfg.SOLVER.BASE_LR = 0.001
cfg.SOLVER.IMS_PER_BATCH = 2  # Adjust this value based on available GPU memory

import torch
torch.cuda.empty_cache()

from detectron2.engine import DefaultTrainer

trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()

cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8   # set the testing threshold for this model
cfg.DATASETS.TEST = ("test_dataset", )
predictor = DefaultPredictor(cfg)

from detectron2.utils.visualizer import ColorMode
import glob
from google.colab.patches import cv2_imshow


for imageName in glob.glob('/content/test_images/*.jpg'):
    im = cv2.imread(imageName)
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1],
                   metadata=train_metadata,
                   scale=0.8
                  )
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2_imshow(out.get_image()[:, :, ::-1])



# Saving the model to drive from Colab

# model_save_name = 'detectron2_maskdetectionv2_abhiraj.pth'

# path = F"/content/drive/MyDrive/Colab Notebooks/Detect2/{model_save_name}"
# torch.save(trainer.model.state_dict(), path)

# f = open('config.yml', 'w')
# f.write(cfg.dump())
# f.close()



# Download the files
from google.colab import files

files.download('/content/output/model_final.pth')
