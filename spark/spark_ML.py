
from pprint import pprint
from pyspark.sql.functions import udf, unix_timestamp, window
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from elasticsearch import Elasticsearch
from pyspark.sql.functions import from_json, col, to_timestamp, unix_timestamp, window
import pyspark.sql.types as tp
import time
from sklearn.linear_model import LinearRegression
from ipwhois import IPWhois
import pandas as pd

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

es_mapping2 = {
    "mappings": {
        "properties": {
            "@timestamp": {"type": "date"},
            "time": {"type": "date"}
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
        # print(owner)
        cache[ip] = owner

    return cache[ip]


es = Elasticsearch(hosts=elastic_host)
while not es.ping():
    time.sleep(1)
es.indices.create(
    index=elastic_index,
    body=es_mapping,
    ignore=400  # ignore 400 already exists code
)

es.indices.create(
    index=elastic_index+"-netstat",
    body=es_mapping2,
    ignore=400  # ignore 400 already exists code
)


def get_resulting_df_schema():
    return tp.StructType() \
        .add("@timestamp",     tp.TimestampType())\
        .add("time",            tp.TimestampType())\
        .add("predict",         tp.IntegerType())


def get_linear_regression_model(df: pd.DataFrame):
    x=df['@timestamp'].to_numpy().reshape(-1, 1)
    y=df['port'].to_numpy()
    lr=LinearRegression()
    print(y)
    lr.fit(x, y)
    return lr


def get_output_df():
    return pd.DataFrame(columns = [
        '@timestamp',
        'time',
        'predict'
    ])

def predict_value(model, milliseconds):
    s=model.predict([[milliseconds]])[0]
    return s


def predict(df: pd.DataFrame) -> pd.DataFrame:
    # print(df)
    df.set_index("@timestamp", inplace = True)
    print(df)
    df_grouped=df.groupby(pd.Grouper(freq="20S"))\
                    .count().reset_index()

    print(df_grouped)
    newdf=get_output_df()

    model=get_linear_regression_model(df_grouped)

    lastTimestamp=df_grouped["@timestamp"].values.max()
    print(lastTimestamp)
    print(type(lastTimestamp))
    next_minutes=[
        (lastTimestamp + pd.Timedelta(f"{(i+1)*10} S")) for i in range(12)]
    next_roba= [predict_value(model, m.value) for m in next_minutes]
    print(next_roba)
    for m, r in zip(next_minutes, next_roba):
        newdf = newdf.append({"@timestamp": lastTimestamp, "time": m, "predict": max(r, 0)}, ignore_index = True)

    print(newdf)
    return newdf

sparkConf= SparkConf().set("spark.app.name", "network-tap")\
    .set("es.nodes", elastic_host)\
    .set("es.port", "9200") \
    .set("spark.scheduler.mode", "FAIR")

sc= SparkContext.getOrCreate(conf = sparkConf)
spark= SparkSession(sc)
spark.sparkContext.setLogLevel("ERROR")

df_kafka= spark\
    .readStream\
    .format("kafka")\
    .option("kafka.bootstrap.servers", kafkaServer)\
    .option("subscribe", elastic_topic)\
    .option("startingOffset", "earliest")\
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
                   dataType=tp.TimestampType(),  nullable=True),
    tp.StructField(name='hostname', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='ip_src', dataType=tp.StringType(),  nullable=True),
    tp.StructField(name='port', dataType=tp.IntegerType(),  nullable=True),
    tp.StructField(name='geoip', dataType=geoip_struct, nullable=True)
])

df_kafka= df_kafka.selectExpr("CAST(value AS STRING)")\
    .select(from_json("value", network_tap).alias("data"))\
    .select("data.*")
df_kafka= df_kafka.withColumn("Owner", getOwner(df_kafka.geoip.ip))


counting= df_kafka\
    .select("@timestamp", "port")\
    .groupBy(window("@timestamp", "2 minutes"))\
    .applyInPandas(predict, get_resulting_df_schema())


df_kafka\
    .writeStream\
    .option("checkpointLocation", "/tmp/checkpoints")\
    .format("es")\
    .start(elastic_index)


counting\
    .writeStream\
    .option("checkpointLocation", "/tmp/checkpoints2")\
    .format("es")\
    .trigger(processingTime = '2 minutes')\
    .start(elastic_index+"-netstat")

spark.streams.awaitAnyTermination()
