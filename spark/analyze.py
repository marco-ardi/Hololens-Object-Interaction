from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import Visualizer
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from pprint import pprint
from pyspark.sql.functions import udf
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from elasticsearch import Elasticsearch
from pyspark.sql.functions import from_json
from pyspark.sql.functions import struct
import pyspark.sql.types as tp
import time
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
from detectron2.data.datasets import register_coco_instances, load_coco_json
setup_logger()


cfg = get_cfg()
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
#cfg.merge_from_file(model_zoo.get_config_file(
#    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.55  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
#cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
#    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")

register_coco_instances("enigma_val", {}, "/usr/share/logstash/csv/Data/val_coco.json", "./") 

dataset_val_dicts = DatasetCatalog.get("enigma_val")
enigma_val_metadata = MetadataCatalog.get("enigma_val")

#cfg.merge_from_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
cfg.merge_from_file("./configs/COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
#cfg.model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
cfg.MODEL.WEIGHTS = os.path.join("/usr/share/logstash/csv/Data/model_final.pth")
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 20

def load_img(path):
    im = cv2.imread(path)
    return im


def predict(im):
    predictor = DefaultPredictor(cfg.value)
    outputs = predictor(im)
    return outputs


# given a tuple (coord) and a predictor (outputs), checks which label are in the nearby (+-20px) of coord
def check_labels(coord, outputs):
    lst = []
    offset = 10

    pred_classes = outputs["instances"].pred_classes.tolist()
    #class_names = MetadataCatalog.get(cfg.value.DATASETS.TRAIN[0]).thing_classes
    class_names = enigma_val_metadata.thing_classes
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
            if(pred_class_names[i] != "mano"):
                lst.append(pred_class_names[i])
    #print(lst)
    return lst


def visualize(im, outputs, id):
    #v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.value.DATASETS.TRAIN[0]), scale=1.2)
    v = Visualizer(im[:, :, ::-1], enigma_val_metadata, scale=1.2)

    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    #[636, 361, 387, 388, 497, 325, 581, 327, 624, 359, 626, 458]
    #cv2.rectangle(im, (636-30, 361-30), (636+30, 361+30), (0,0,0), 10)
    #cv2.imshow(out.get_image()[:, :, ::-1])
    cv2.imwrite("/usr/share/logstash/csv/output_imgs/detected_"+id+".jpg", out.get_image()[:, :, ::-1])


def apply_detectron_row_modified(kafka_row):
    df_labels = list(enigma_val_metadata.thing_classes)
    #print(list(enigma_val_metadata.thing_classes))
    #print(result_schema.fieldNames())
    #df_labels=result_schema.fieldNames()
    #print(df_labels)
    #print(type(kafka_row))
    kafka_row = kafka_row.asDict()
    kafka_row = list(kafka_row.values())
    
    gaze_labels = []
    hand_labels = []

    # load img
    id = str(kafka_row[0])
    print(kafka_row[0])
    print("id =" + id)

    if(not os.path.isfile("/usr/share/logstash/csv/input_imgs/" + id + ".jpg")):#check if photos exists, if not return 0
        #return list([id] + [0 for x in range(len(df_labels)-1)])     #cause otherwise it will crash
        print("non trovo l'immagine")
        return {"id":id, "classes":""}
    tmp_img = load_img("/usr/share/logstash/csv/input_imgs/" + id + ".jpg")
    print(tmp_img.shape)
    tmp_outputs = predict(tmp_img)

    #first tuple is gaze
    gaze_labels += check_labels(coord=[kafka_row[1], kafka_row[2]], outputs=tmp_outputs)
    #then 10 tuple for hand fingers
    for j in range(3, len(kafka_row)-1, 2):   
    # search in the nearby of coordinates  1-2  2-3  3-4
        if(kafka_row[j] >= 0 and kafka_row[j+1] >= 0):  # filtering <0 values and NaN
            hand_labels += check_labels(coord=[kafka_row[j], kafka_row[j+1]], outputs=tmp_outputs)
    
    #now we save detected img
    visualize(tmp_img, tmp_outputs, id)

    gaze_labels = set (gaze_labels)
    hand_labels = set(hand_labels)
    #labels.add(id)
    df_labels = set(df_labels)
    gaze_row_to_append = gaze_labels & df_labels
    hand_row_to_append = hand_labels & df_labels
    
    
    pred_classes = tmp_outputs["instances"].pred_classes.tolist()
    #class_names = MetadataCatalog.get(cfg.value.DATASETS.TRAIN[0]).thing_classes
    class_names = enigma_val_metadata.thing_classes
    pred_class_names = list(map(lambda x: class_names[x], pred_classes))

    object_in_scene = set(pred_class_names)


    result = {
        "id":id,
        "Looked at": list(gaze_row_to_append),
        "Interacted with": list(hand_row_to_append),
        "Object in scene": list(object_in_scene)
    }

    print(result)
    return result



#Version 2.0 id and list of classes
es_mapping_modified = {
    "mappings":{
        "properties":{
            "id":{"type":"date"},
            #"classes":{"type":"text"}
        }
    }
}

kafkaServer = "kafkaserver:9092"
elastic_host = "elasticsearch"

elastic_topic = "tap"
elastic_index = "tap"

es = Elasticsearch(hosts=elastic_host)
while not es.ping():
    time.sleep(1)

es.indices.create(
    index=elastic_index,
    body=es_mapping_modified,
    ignore=400  # ignore 400 already exists code
)


#Configuring Spark
sparkConf = SparkConf().set("spark.app.name", "network-tap") \
    .set("es.nodes", elastic_host) \
    .set("es.port", "9200") \
    .set("spark.executor.heartbeatInterval", "200000") \
    .set("spark.network.timeout", "300000")

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")
#MANDATORY 
cfg = spark.sparkContext.broadcast(cfg)
dataset_val_dicts = spark.sparkContext.broadcast(dataset_val_dicts)
dataset_val_dicts = spark.sparkContext.broadcast(dataset_val_dicts)


data_struct = tp.StructType([
    tp.StructField(name="id", dataType=tp.StringType(), nullable=True),
    tp.StructField(name="c1", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c2", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c3", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c4", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c5", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c6", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c7", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c8", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c9", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c10", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c11", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c12", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c13", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c14", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c15", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c16", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c17", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c18", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c19", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c20", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c21", dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name="c22", dataType=tp.IntegerType(), nullable=True)
])


#Version 2.0
result_schema_modified =tp.StructType([
    tp.StructField(name="id", dataType=tp.StringType(), nullable=True),
    tp.StructField(name="Looked at", dataType=tp.ArrayType(tp.StringType()), nullable=True),
    tp.StructField(name="Interacted with", dataType=tp.ArrayType(tp.StringType()), nullable=True),
    tp.StructField(name="Object in scene", dataType=tp.ArrayType(tp.StringType()), nullable=True)
])

#Declaring apply_detectron as user defined function
apply_udf = udf(apply_detectron_row_modified, result_schema_modified)

#reading kafka stream
df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", elastic_topic) \
    .option("startingOffset", "earliest") \
    .load()

#selecting data
df_kafka = df_kafka.selectExpr("CAST(value AS STRING)")\
    .select(from_json("value", data_struct).alias("data"))\
    .select("data.*")

#applying detectron on a single row, coming from kafka
df_kafka = df_kafka \
    .select(apply_udf(struct([df_kafka[x] for x in df_kafka.columns])).alias("result")) \
    .select("result.*")

#outputting list of classes to elastic searc
df_kafka \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .format("es") \
    .start(elastic_index) \
    .awaitTermination()

#http://localhost:5601/app/dashboards#/view/2f397610-0fcd-11ec-95f7-3995aa48d6d7?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A2000)%2Ctime%3A(from%3A'2021-08-01T11%3A00%3A51.458Z'%2Cto%3A'2021-08-03T11%3A15%3A57.505Z'))