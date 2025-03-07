# -*- coding: utf-8 -*-
"""CHARACTERIZATION OF BIM ROCKS WITH ARTIFICIAL INTELLIGENCE AND DEEP LEARNING.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hnqKbu9WQNPVkEY-It8LCbPwjuNXaAgu

## Segmentation model using Detectron2

https://www.makesense.ai/

**Install Detectron2**
"""

# Install pyyaml
!python -m pip install pyyaml==5.1

import sys, os, distutils.core
# Note: This is a faster way to install detectron2 in Colab, but it does not include all functionalities (e.g. compiled operators).
# See https://detectron2.readthedocs.io/tutorials/install.html for full installation instructions
!git clone 'https://github.com/facebookresearch/detectron2'
dist = distutils.core.run_setup("./detectron2/setup.py")
!python -m pip install {' '.join([f"'{x}'" for x in dist.install_requires])}
sys.path.insert(0, os.path.abspath('./detectron2'))

# Properly install detectron2. (Please do not install twice in both ways)
# !python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

import torch, detectron2
!nvcc --version
TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
print("detectron2:", detectron2.__version__)

# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

"""#Load Dataset

Import the necessary function to register datasets in the COCO format. Let us register both the training and validation datasets. Please note that we are working with training (and validation) data that is is the coco format where we have a single JSON file that describes all the annotations from all training images. <p>
Here, we are naming our training data as 'my_dataset_train' and the validation data as 'my_dataset_val'.
"""

from google.colab import drive
drive.mount('/content/drive')

from os import listdir
from os.path import isfile, join
from detectron2.data.datasets import register_coco_instances
from detectron2.data import MetadataCatalog, DatasetCatalog

# Definir la ruta a la carpeta que contiene los archivos JSON y las imágenes de entrenamiento
train_folder_path = "/content/drive/MyDrive/DATASET/train"

# Lista para almacenar los nombres de los conjuntos de datos registrados de entrenamiento
train_dataset_names = []

# Función para registrar conjuntos de datos COCO desde la carpeta de entrenamiento
def register_train_dataset(dataset_names, folder_path):
    # Obtener la lista de archivos JSON en la carpeta de entrenamiento
    json_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith('.json')]

    # Iterar sobre cada archivo JSON y registrar los conjuntos de datos en Detectron2
    for json_file in json_files:
        dataset_name = f"{folder_path}_{json_file.split('.')[0]}"  # Nombre del conjunto de datos con prefijo de carpeta
        json_path = join(folder_path, json_file)
        image_root = folder_path  # Ruta raíz de las imágenes (ajustar según la estructura de tu nube)

        # Usar el método público 'remove' para anular el registro del conjunto de datos si ya está registrado
        if dataset_name in DatasetCatalog.list():
            DatasetCatalog.remove(dataset_name)
            MetadataCatalog.remove(dataset_name)

        # Registrar el conjunto de datos en Detectron2
        register_coco_instances(dataset_name, {}, json_path, image_root)
        dataset_names.append(dataset_name)

        print(f"Registrado conjunto de datos de entrenamiento '{dataset_name}' desde '{json_path}'")

# Registrar el conjunto de datos de entrenamiento
register_train_dataset(train_dataset_names, train_folder_path)

# Acceder a los metadatos y los diccionarios de conjuntos de datos de entrenamiento registrados
for dataset_name in train_dataset_names:
    train_metadata = MetadataCatalog.get(dataset_name)
    DatasetCatalog.get(dataset_name)
    train_dataset_dicts = DatasetCatalog.get(dataset_name)
    print(f"Metadatos para '{dataset_name}': {train_metadata}")
    print(f"Datos de conjunto para '{dataset_name}': {len(train_dataset_dicts)} ejemplos")

"""Let us extract the metadata and dataset dictionaries for both training and validation datasets. These can be used later for other purposes, like visualization, model training, evaluation, etc. We will see a visualization example right away."""

# Definir la ruta a la carpeta que contiene los archivos JSON y las imágenes de validación
val_folder_path = "/content/drive/MyDrive/DATASET/val"

# Lista para almacenar los nombres de los conjuntos de datos registrados de validación
val_dataset_names = []

# Función para registrar conjuntos de datos COCO desde la carpeta de validación
def register_val_dataset(dataset_names, folder_path):
    # Obtener la lista de archivos JSON en la carpeta de validación
    json_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith('.json')]

    # Iterar sobre cada archivo JSON y registrar los conjuntos de datos en Detectron2
    for json_file in json_files:
        dataset_name_val = f"{folder_path}_{json_file.split('.')[0]}"  # Nombre del conjunto de datos con prefijo de carpeta
        json_path = join(folder_path, json_file)
        image_root = folder_path  # Ruta raíz de las imágenes (ajustar según la estructura de tu nube)

        # Usar el método público 'remove' para anular el registro del conjunto de datos si ya está registrado
        if dataset_name_val in DatasetCatalog.list():
            DatasetCatalog.remove(dataset_name_val)
            MetadataCatalog.remove(dataset_name_val)

        # Registrar el conjunto de datos en Detectron2
        register_coco_instances(dataset_name_val, {}, json_path, image_root)
        dataset_names.append(dataset_name_val)

        print(f"Registrado conjunto de datos de validación '{dataset_name_val}' desde '{json_path}'")

# Registrar el conjunto de datos de validación
register_val_dataset(val_dataset_names, val_folder_path)

# Acceder a los metadatos y los diccionarios de conjuntos de datos de validación registrados
for dataset_name_val in val_dataset_names:
    val_metadata = MetadataCatalog.get(dataset_name_val)
    DatasetCatalog.get(dataset_name_val)
    val_dataset_dicts = DatasetCatalog.get(dataset_name_val)
    print(f"Metadatos para '{dataset_name_val}': {val_metadata}")
    print(f"Datos de conjunto para '{dataset_name_val}': {len(val_dataset_dicts)} ejemplos")

"""# Data Division"""

from matplotlib import pyplot as plt

# Visualize some random samples
for d in random.sample(train_dataset_dicts, 2):
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=train_metadata, scale=0.5)
    vis = visualizer.draw_dataset_dict(d)
    plt.imshow(vis.get_image()[:, :, ::-1])
    plt.show()

"""# Model Configuration

Now we are ready to train a Mask R-CNN model using the Detectron2 library. We start by setting up a configuration file (.cfg) for the model. The configuration file contains many details including the output directory path, training dataset information, pre-trained weights, base learning rate, maximum number of iterations, etc.
"""

from detectron2.engine import DefaultTrainer

cfg = get_cfg()
cfg.OUTPUT_DIR = "/content/drive/MyDrive/ENTRENADOS"
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = (dataset_name)
cfg.DATASETS.TEST = ()
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # Let training initialize from model zoo
cfg.SOLVER.IMS_PER_BATCH = 2  # This is the real "batch size" commonly known to deep learning people
cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
cfg.SOLVER.MAX_ITER = 400    # 1000 iterations seems good enough for this dataset
cfg.SOLVER.STEPS = []        # do not decay learning rate
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256   # Default is 512, using 256 for this dataset.
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4  # We have 4 classes.
# NOTE: this config means the number of classes, without the background. Do not use num_classes+1 here.

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = DefaultTrainer(cfg) #Create an instance of of DefaultTrainer with the given congiguration
trainer.resume_or_load(resume=False) #Load a pretrained model if available (resume training) or start training from scratch if no pretrained model is available

"""# Model Training"""

trainer.train() #Start the training process

"""Save the config file, for potential future use"""

# Commented out IPython magic to ensure Python compatibility.
# Look at training curves in tensorboard:
# %load_ext tensorboard
# %tensorboard --logdir output

import yaml
# Save the configuration to a config.yaml file
# Save the configuration to a config.yaml file
config_yaml_path = "/content/drive/MyDrive/ENTRENADOS/config.yaml"
with open(config_yaml_path, 'w') as file:
    yaml.dump(cfg, file)

"""# Evaluation of the trained model"""

# Inference should use the config with parameters that are used in training
# cfg now already contains everything we've set previously. We changed it a little bit for inference:
cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # path to the model we just trained
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2   # set a custom testing threshold
predictor = DefaultPredictor(cfg)

"""Verify segmentation on random validation images"""

from detectron2.utils.visualizer import ColorMode

for d in random.sample(val_dataset_dicts, 2):    #select number of images for display
    im = cv2.imread(d["file_name"])
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1],
                   metadata=val_metadata,
                   scale=0.5,
                   instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels. This option is only available for segmentation models
    )
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2_imshow(out.get_image()[:, :, ::-1])

"""Check average precision and recall. (Need more validation data than just 2 images with handful of annotations)"""

from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader
evaluator = COCOEvaluator(dataset_name_val, output_dir="./output")
val_loader = build_detection_test_loader(cfg, dataset_name_val)
print(inference_on_dataset(predictor.model, val_loader, evaluator))
# another equivalent way to evaluate the model is to use `trainer.test`

"""**Load a new image and segment it.**"""

new_im = cv2.imread("/content/drive/MyDrive/IMAGENES/24.png")
outputs  = predictor(new_im)

# We can use `Visualizer` to draw the predictions on the image.
v = Visualizer(new_im[:, :, ::-1], metadata=train_metadata)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

cv2_imshow(out.get_image()[:, :, ::-1])

"""# Measurement of percentage volume of rocks"""

# Calcular el área total de la imagen
total_area = new_im.shape[0] * new_im.shape[1]  # Altura x Ancho

# Calcular el área ocupada por las instancias de roca
instances = outputs["instances"]
areas_roca = []
# Check if 'pred_classes' exists and use it instead of 'prediction_classes'
if hasattr(instances, 'pred_classes'):
    for i in range(len(instances)):
        if train_metadata.thing_classes[instances.pred_classes[i]] == "roca":  # Ajusta la clase según tus datos
            area = instances.pred_boxes.area()[i].item()
            areas_roca.append(area)
else:
    print("Warning: 'pred_classes' not found in Instances object. Check predictor output.")

area_ocupada_roca = sum(areas_roca)

# Calcular el porcentaje de volumen de roca
porcentaje_roca = (area_ocupada_roca / total_area) * 100

# Definir los límites para clasificar las categorías
limite_bajo = 25
limite_alto = 75

# Clasificar según el porcentaje de volumen de roca
if porcentaje_roca < limite_bajo:
    categoria_roca = "matriz"
elif porcentaje_roca >= limite_bajo and porcentaje_roca <= limite_alto:
    categoria_roca = "BIM rock"
else:
    categoria_roca = "macizo rocoso"

# Imprimir el resultado
print(f"Porcentaje de volumen de roca en la imagen: {porcentaje_roca:.2f}%")
print(f"Categoría de roca: {categoria_roca}")