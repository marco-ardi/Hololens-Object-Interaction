[![CodeFactor](https://www.codefactor.io/repository/https://github.com/marco-ardi/Hololens-Object-Interaction/badge)](https://www.codefactor.io/repository/https://github.com/marco-ardi/Hololens-Object-Interaction)
# Hololens Object Interaction

## Overview
Project for Bachelor Thesis @ University of Catania.

![](https://user-images.githubusercontent.com/50525101/145630275-f66cb3f6-da47-4fd2-8ac3-27501d30881d.png)


A Pipeline for real time object detection/interaction on data coming from a data source (Microsoft Hololens2) using ELK Stack.
A pair of Hololens2 sends, once per 2/3 seconds, a photo and a formatted log about eye gaze and hand position, via a TCP socket.
A socket server (python) receives these data, convert logs into 2D logs and stores on a Docker Volume.
Logstash reads from this volume and sends data to Apache Kafka, used for Data Collection.
Kafka acts as queue and sends a stream of data to Spark.
Spark (pySpark) applies [Detectron2](https://github.com/facebookresearch/detectron2) on the photo and checks whether there is a bounding box in the nearby of hand joints/eye gaze coordinates: if yes, that is an interaction and a list of interacted object is sent to ElasticSearch.
ElastiSearch is used for Data Indexing, these data are then used by Kibana for showing dashboard and insights.
These dashboard can also be seen in AR on Hololens2

## How to setup 
#### System requirement:
- Linux/MacOS/Windows WSL2.
- Nvidia GPU (mandatory for using [Detectron2.](https://github.com/facebookresearch/detectron2))
- Nvidia drivers/CUDA toolkit 11.1
- 🐋Docker/Docker-compose
- python 3.7 with following modules:
  -  openCV.
  -  Flask.
  -  Selenium.

#### Steps
- Clone this repository
- **Run** `cd FlaskWebServer`
- **Run** `bash runapp.sh`
- **Run** `cd ../logstash`
- **Run** `python serverPy.py`

