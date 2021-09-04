from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import Visualizer
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
import numpy as np
import os
import json
import cv2
import random
import pandas as pd
import torch
import torchvision
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()


cfg = get_cfg()
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.55  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)


def load_img(path):
    im = cv2.imread(path)
    return im


def predict(im):
    outputs = predictor(im)
    return outputs


# given a tuple (coord) and a predictor (outputs), checks which label are in the nearby (+-20px) of coord
def check_labels(coord, outputs):
    lst = []
    offset = 10

    pred_classes = outputs["instances"].pred_classes.tolist()
    class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes
    pred_class_names = list(map(lambda x: class_names[x], pred_classes))

    for i in range(len(outputs["instances"].pred_boxes)):
        if((
            (coord[0]-offset >= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][0] and
             coord[0]-offset <= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][0] + outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][2]) and
          (coord[1]-offset >= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][1] and
                coord[1]-offset <= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][1] + outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][3])
        )
            or
            (coord[0]+offset >= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][0] and
             coord[0]+offset <= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][0] + outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][2]) and
            (coord[1]+offset >= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][1] and
             coord[1]+offset <= outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][1] + outputs["instances"].pred_boxes[i].tensor.cpu().numpy()[0][3])
        ):
            if(pred_class_names[i] != "person"):
                lst.append(pred_class_names[i])

    return lst


def visualize(im, outputs):
    v = Visualizer(
        im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)

    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    #[636, 361, 387, 388, 497, 325, 581, 327, 624, 359, 626, 458]
    #cv2.rectangle(im, (636-30, 361-30), (636+30, 361+30), (0,0,0), 10)
    cv2.imshow(out.get_image()[:, :, ::-1])
    #cv2.imwrite( "/content/detected_wrong.jpg", out.get_image()[:, :, ::-1])


def apply_detectron_row(kafka_row):
    print("palagonia")
    print(kafka_row)
   
    df_labels=["id","person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic_light","fireplug","stop_sign","parking_meter","bench","bird","cat","dog","horse","sheep","beef","elephant","bear","zebra","giraffe","backpack","umbrella","bag","necktie","bag","frisbee","ski","snowboard","ball","kite","baseball_bat","baseball_glove","skateboard","surfboard","tennis_racket","bottle","wineglass","cup","fork","knife","spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","frank","pizza","doughnut","cake","chair","sofa","pot","bed","dining_table","toilet","television_receiver","laptop","mouse","remote_control","computer_keyboard","cellular_telephone","microwave","oven","toaster","sink","electric_refrigerator","book","clock","vase","scissors","teddy","hand_blower"",""toothbrush"]
    #print(list(map(lambda a : result_schema[:[0]]"","" result_schema)))
    
    print(type(kafka_row))
    #print(list(row.asDict()))
    labels = []

    # load img
    id = str(kafka_row[0])
    print("id=" + id)
    tmp_img = load_img("/home/marco/progetto/logstash/csv/" + id + ".jpg")
    #cv2.imshow(tmp_img)
    tmp_outputs = predict(tmp_img)
 
#    for coord_x, coord_y in zip(kafka_row, kafka_row[1:]):
#        if coord_x < 0 or coord_y < 0:
#            continue
#        labels += check_labels(coord=[coord_x, coord_y], outputs=tmp_outputs)

    final_labels = [] #final_labels inutile, basta labels
    for j in range(1, len(kafka_row)-1):   
    # search in the nearby of coordinates  1-2  2-3  3-4
        if(kafka_row[j] >= 0 and kafka_row[j+1] >= 0):  # filtering <0 values and NaN
            labels += check_labels(coord=[kafka_row[j], kafka_row[j+1]], outputs=tmp_outputs)
            final_labels += labels
        j+=1

    final_labels = list(set(labels))
    final_labels.sort()
    final_labels.insert(0, id)

    row_to_append = []
    row_to_append.append(id)
    for w in range(1, len(df_labels)):
        row_to_append.append(0)

    for i in range(1, len(final_labels)):
        for j in range(1, len(df_labels)):
            if(final_labels[i] == df_labels[j]):
                row_to_append[j] = 1
                continue

    
    print(row_to_append)
    print(final_labels)
    print(df_labels)
    return row_to_append

apply_detectron_row(["1627914023594",636,361,552,630,483,606,427,567,353,570,255,620,695,650,761,602,818,568,898,554,1013,580])



