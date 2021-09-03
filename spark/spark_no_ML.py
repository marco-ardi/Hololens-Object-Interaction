
from pprint import pprint
from pyspark.sql.functions import udf
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from elasticsearch import Elasticsearch
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
import time
from ipwhois import IPWhois

#SENZA ML   

kafkaServer = "kafkaserver:9092"
elastic_host = "elasticsearch"

elastic_topic = "tap"
elastic_index = "tap"

es_mapping = {
    "mappings": {
        "properties": {
            "@timestamp": {"type": "date"},
            "ip_src": {"type": "ip"},
            "geoip": {
                "properties": {
                    "ip": {"type": "ip"},
                    "location": {"type": "geo_point"}
                }
            }
        }
    }
}
cache = {}

@udf
def getOwner(ip):
    # pprint(ip)
    if ip is None:
        return "Unknown"
    if ip not in cache:
        res = IPWhois(ip).lookup_whois()
        owner = res["nets"][0]["description"]
        if owner is None:
            owner = res["nets"][0]["name"]
            print(owner)
        cache[ip] = owner

    return cache[ip]


es = Elasticsearch(hosts=elastic_host)
while not es.ping():
    time.sleep(1)

response = es.indices.create(
    index=elastic_index,
    body=es_mapping,
    ignore=400  # ignore 400 already exists code
)

sparkConf = SparkConf().set("spark.app.name", "network-tap") \
    .set("es.nodes", elastic_host) \
    .set("es.port", "9200") \

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")

df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", elastic_topic) \
    .option("startingOffset", "earliest") \
    .load()

location_struct = tp.StructType([
    tp.StructField(name='lat', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='lon', dataType=tp.StringType(),  nullable=True)
])
geoip_struct = tp.StructType([
    tp.StructField(name='ip', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='location', dataType=location_struct,  nullable=True),
    tp.StructField(name='country_name',
                   dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='continent_code',
                   dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='country_code2',
                   dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='dma_code', dataType=tp.IntegerType(),  nullable=True),
    tp.StructField(name='region_name',
                   dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='city_name', dataType=tp.StringType(),  nullable=True)
])

network_tap = tp.StructType([
    tp.StructField(name='@timestamp',
                   dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='hostname', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='ip_src', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='port', dataType=tp.IntegerType(),  nullable=True),
    tp.StructField(name='geoip', dataType=geoip_struct, nullable=True)
])

df_kafka = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", network_tap).alias("data"))\
    .select("data.*")

#print(getOwner(df_kafka.geoip.ip))
df_kafka = df_kafka.withColumn("Owner", getOwner(df_kafka.geoip.ip))

df_kafka = df_kafka.writeStream \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .format("es") \
    .start(elastic_index) \
    .awaitTermination()
