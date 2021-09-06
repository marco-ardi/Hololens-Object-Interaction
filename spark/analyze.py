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
setup_logger()


cfg = get_cfg()
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.55  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")



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
    class_names = MetadataCatalog.get(cfg.value.DATASETS.TRAIN[0]).thing_classes
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
        im[:, :, ::-1], MetadataCatalog.get(cfg.value.DATASETS.TRAIN[0]), scale=1.2)

    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    #[636, 361, 387, 388, 497, 325, 581, 327, 624, 359, 626, 458]
    #cv2.rectangle(im, (636-30, 361-30), (636+30, 361+30), (0,0,0), 10)
    cv2.imshow(out.get_image()[:, :, ::-1])
    #cv2.imwrite( "/content/detected_wrong.jpg", out.get_image()[:, :, ::-1])



#["id", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14", "c15", "c16", "c17", "c18", "c19", "c20", "c21", "c22"]

def apply_detectron_row(kafka_row):
    #print(kafka_row)
    #print(kafka_row.asDict())
    #print(list(kafka_row.asDict().values()))
    #print(list(result_schema))
    df_labels=result_schema.fieldNames()
    #print(df_labels)

    
    #print(type(kafka_row))
    kafka_row = kafka_row.asDict()
    kafka_row = list(kafka_row.values())

    labels = []

    id = str(kafka_row[0])
    print(kafka_row[0])
    print("id =" + id)

    if(not os.path.isfile("/usr/share/logstash/csv/" + id + ".jpg")):#check if photos exists, if not return 0
        return list([id] + [0 for x in range(len(df_labels)-1)])     #cause otherwise it will crash

    tmp_img = load_img("/usr/share/logstash/csv/" + id + ".jpg")
    print(tmp_img.shape)
    tmp_outputs = predict(tmp_img)

    for j in range(1, len(kafka_row)-1):   
    # search in the nearby of coordinates  1-2  2-3  3-4
        if(kafka_row[j] >= 0 and kafka_row[j+1] >= 0):  # filtering <0 values and NaN
            labels += check_labels(coord=[kafka_row[j], kafka_row[j+1]], outputs=tmp_outputs)
        j+=1

    labels = list(set(labels))
    labels.sort()
    labels.insert(0, id)
    row_to_append = []
    row_to_append.append(id)
    for w in range(1, len(df_labels)):
        row_to_append.append(0)

    for i in range(1, len(labels)):
        for j in range(1, len(df_labels)):
            if(labels[i] == df_labels[j]):
                row_to_append[j] = 1
                continue

    #print(row_to_append)
    return row_to_append


def apply_detectron_row_modified(kafka_row):
    #print(kafka_row)
    #print(kafka_row.asDict())
    #print(list(kafka_row.asDict().values()))
    #print(list(result_schema))
    df_labels=result_schema.fieldNames()
    #print(df_labels)

    
    #print(type(kafka_row))
    kafka_row = kafka_row.asDict()
    kafka_row = list(kafka_row.values())

    labels = []

    # load img
    id = str(kafka_row[0])
    print(kafka_row[0])
    print("id =" + id)

    if(not os.path.isfile("/usr/share/logstash/csv/" + id + ".jpg")):#check if photos exists, if not return 0
        #return list([id] + [0 for x in range(len(df_labels)-1)])     #cause otherwise it will crash
        return {"id":id, "classes":""}
    tmp_img = load_img("/usr/share/logstash/csv/" + id + ".jpg")
    print(tmp_img.shape)
    tmp_outputs = predict(tmp_img)

    for j in range(1, len(kafka_row)-1):   
    # search in the nearby of coordinates  1-2  2-3  3-4
        if(kafka_row[j] >= 0 and kafka_row[j+1] >= 0):  # filtering <0 values and NaN
            labels += check_labels(coord=[kafka_row[j], kafka_row[j+1]], outputs=tmp_outputs)
        j+=1
#    for coord_x, coord_y in zip(kafka_row, kafka_row[1:]):
#        if coord_x<0 or coord_y <0:
#            continue
#        labels += check_labels(coord=[coord_x, coord_y], outputs=tmp_outputs)

    labels = set(labels)
    #labels.add(id)
    df_labels = set(df_labels)
    row_to_append = labels & df_labels
    result = {
        "id":id,
        "classes": list(row_to_append)
    }

    print(result)
    return result


kafkaServer = "kafkaserver:9092"
elastic_host = "elasticsearch"

elastic_topic = "tap"
elastic_index = "tap"

es_mapping = {
    "mappings":{
        "properties":{
            "id":{"type":"date"},
            "person":{"type":"integer"},
            "bicycle":{"type":"integer"},
            "car":{"type":"integer"},
            "motorcycle":{"type":"integer"},
            "airplane":{"type":"integer"},
            "bus":{"type":"integer"},
            "train":{"type":"integer"},
            "truck":{"type":"integer"},
            "boat":{"type":"integer"},
            "traffic_light":{"type":"integer"},
            "fireplug":{"type":"integer"},
            "stop_sign":{"type":"integer"},
            "parking_meter":{"type":"integer"},
            "bench":{"type":"integer"},
            "bird":{"type":"integer"},
            "cat":{"type":"integer"},
            "dog":{"type":"integer"},
            "horse":{"type":"integer"},
            "sheep":{"type":"integer"},
            "beef":{"type":"integer"},
            "elephant":{"type":"integer"},
            "bear":{"type":"integer"},
            "zebra":{"type":"integer"},
            "giraffe":{"type":"integer"},
            "backpack":{"type":"integer"},
            "umbrella":{"type":"integer"},
            "bag":{"type":"integer"},
            "necktie":{"type":"integer"},
            "bag2":{"type":"integer"},
            "frisbee":{"type":"integer"},
            "ski":{"type":"integer"},
            "snowboard":{"type":"integer"},
            "ball":{"type":"integer"},
            "kite":{"type":"integer"},
            "baseball_bat":{"type":"integer"},
            "baseball_glove":{"type":"integer"},
            "skateboard":{"type":"integer"},
            "surfboard":{"type":"integer"},
            "tennis_racket":{"type":"integer"},
            "bottle":{"type":"integer"},
            "wineglass":{"type":"integer"},
            "cup":{"type":"integer"},
            "fork":{"type":"integer"},
            "knife":{"type":"integer"},
            "spoon":{"type":"integer"},
            "bowl":{"type":"integer"},
            "banana":{"type":"integer"},
            "apple":{"type":"integer"},
            "sandwich":{"type":"integer"},
            "orange":{"type":"integer"},
            "broccoli":{"type":"integer"},
            "carrot":{"type":"integer"},
            "frank":{"type":"integer"},
            "pizza":{"type":"integer"},
            "doughnut":{"type":"integer"},
            "cake":{"type":"integer"},
            "chair":{"type":"integer"},
            "sofa":{"type":"integer"},
            "pot":{"type":"integer"},
            "bed":{"type":"integer"},
            "dining_table":{"type":"integer"},
            "toilet":{"type":"integer"},
            "television_receiver":{"type":"integer"},
            "laptop":{"type":"integer"},
            "mouse":{"type":"integer"},
            "remote_control":{"type":"integer"},
            "computer_keyboard":{"type":"integer"},
            "cellular_telephone":{"type":"integer"},
            "microwave":{"type":"integer"},
            "oven":{"type":"integer"},
            "toaster":{"type":"integer"},
            "sink":{"type":"integer"},
            "electric_refrigerator":{"type":"integer"},
            "book":{"type":"integer"},
            "clock":{"type":"integer"},
            "vase":{"type":"integer"},
            "scissors":{"type":"integer"},
            "teddy":{"type":"integer"},
            "hand_blower":{"type":"integer"},
            "toothbrush":{"type":"integer"},
        }
    }
}


es_mapping_modified = {
    "mappings":{
        "properties":{
            "id":{"type":"date"},
            #"classes":{"type":"text"}
        }
    }
}

es = Elasticsearch(hosts=elastic_host)
while not es.ping():
    time.sleep(1)

es.indices.create(
    index=elastic_index,
    body=es_mapping_modified,
    ignore=400  # ignore 400 already exists code
)


# sessione spark
#    .set("spark.executor.heartbeatInterval", "200000") \
#    .set("spark.network.timeout", "300000") \
sparkConf = SparkConf().set("spark.app.name", "network-tap") \
    .set("es.nodes", elastic_host) \
    .set("es.port", "9200") \
    .set("spark.executor.heartbeatInterval", "200000") \
    .set("spark.network.timeout", "300000")

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")
#ADDED
cfg = spark.sparkContext.broadcast(cfg)

# leggere da kafka
df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", elastic_topic) \
    .option("startingOffset", "earliest") \
    .load()

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

result_schema = tp.StructType([
    tp.StructField(name="id", dataType=tp.StringType(), nullable=True),
    tp.StructField(name='person', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bicycle', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='car', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='motorcycle', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='airplane', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bus', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='train', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='truck', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='boat', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='traffic_light', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='fireplug', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='stop_sign', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='parking_meter', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bench', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bird', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='cat', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='dog', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='horse', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='sheep', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='beef', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='elephant', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bear', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='zebra', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='giraffe', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='backpack', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='umbrella', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bag', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='necktie', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bag2', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='frisbee', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='ski', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='snowboard', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='ball', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='kite', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='baseball_bat', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='baseball_glove', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='skateboard', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='surfboard', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='tennis_racket', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bottle', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='wineglass', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='cup', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='fork', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='knife', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='spoon', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bowl', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='banana', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='apple', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='sandwich', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='orange', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='broccoli', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='carrot', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='frank', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='pizza', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='doughnut', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='cake', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='chair', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='sofa', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='pot', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='bed', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='dining_table', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='toilet', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='television_receiver', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='laptop', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='mouse', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='remote_control', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='computer_keyboard', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='cellular_telephone', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='microwave', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='oven', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='toaster', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='sink', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='electric_refrigerator', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='book', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='clock', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='vase', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='scissors', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='teddy', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='hand_blower', dataType=tp.IntegerType(), nullable=True),
    tp.StructField(name='toothbrush', dataType=tp.IntegerType(), nullable=True)
])

result_schema_modified =tp.StructType([
    tp.StructField(name="id", dataType=tp.StringType(), nullable=True),
    tp.StructField(name="classes", dataType=tp.ArrayType(tp.StringType()), nullable=True)
])


apply_udf = udf(apply_detectron_row_modified, result_schema_modified)
#apply_udf = udf(useless, result_schema)

df_kafka = df_kafka.selectExpr("CAST(value AS STRING)")\
    .select(from_json("value", data_struct).alias("data"))\
    .select("data.*")


df_kafka = df_kafka \
    .select(apply_udf(struct([df_kafka[x] for x in df_kafka.columns])).alias("result")) \
    .select("result.*")


#df_kafka = df_kafka\
#    .select(apply_udf(df_kafka).alias("decoded").select("decoded.*"))


df_kafka \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .format("es") \
    .start(elastic_index) \
    .awaitTermination()
# .option("checkpointLocation", "/tmp/checkpoints") \
# .outputMode("append") \
#spark.streams.awaitAnyTermination()
#http://localhost:5601/app/dashboards#/view/fe8bacf0-0e72-11ec-adf3-e16766a3809f?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!f%2Cvalue%3A5000)%2Ctime%3A(from%3A'2021-08-02T12%3A00%3A00.000Z'%2Cto%3A'2021-08-02T17%3A30%3A00.000Z'))