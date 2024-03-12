# Based on this consumer: https://github.com/5gmeta/stream-data-gateway/blob/main/examples/consumer/cits-kafka-consumer.py

# Some sample code for the cosumere can be find 
# here https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/json_consumer.py

import keycloak
from confluent_kafka import Consumer, KafkaException
import sys
import getopt
import json
import logging
from pprint import pformat
import time
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.cimpl import TopicPartition
import sys
import base64

import requests

import proton

platformaddress = "5gmeta-platform.eu"
bootstrap_port = "9092"
registry_port =  "8081"
dataflowapi_port = "443"

# Url to request a topic containing cits messages with subtype cam and with in the quadkey 123012301230123
url = "https://"+platformaddress+':'+dataflowapi_port+'/dataflow-api/topics/cits/query?dataSubType=denm&instance_type=small&quadkey=12022301011101'

# This header should NOT be added by the application, but by APISIX  
# headers = {
#     "X-Userinfo": "eyJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwianRpIjoiNTIxMjYzZTQtNjMxYy00MjMzLTlkMjktNGMxMzk1NGJlNzhmIiwic2lkIjoiZTMzMGNmNTctMTVlYy00Njc0LTljOTQtMmVkNGY4YzUwNzM5Iiwic3ViIjoiYTQ1YjhiNDYtMzg5NC00YTIxLThkZGYtZWY5NDQxMmNmMGFjIiwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidXNlcjEiLCJhenAiOiI1Z21ldGFfbG9naW4iLCJzZXNzaW9uX3N0YXRlIjoiZTMzMGNmNTctMTVlYy00Njc0LTljOTQtMmVkNGY4YzUwNzM5IiwiYWN0aXZlIjp0cnVlLCJ0eXAiOiJCZWFyZXIiLCJ1c2VybmFtZSI6InVzZXIxIiwiZXhwIjoxNjQ5OTI1MTI5LCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImFjciI6IjEiLCJpc3MiOiJodHRwczpcL1wvaWRlbnRpdHktNWdtZXRhLndlc3RldXJvcGUuY2xvdWRhcHAuYXp1cmUuY29tOjg0NDNcL3JlYWxtc1wvNWdtZXRhIiwiYXVkIjoiYWNjb3VudCIsImlhdCI6MTY0OTkyNDgyOSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0LXJvbGVzLTVnbWV0YSJdfSwiY2xpZW50X2lkIjoiNWdtZXRhX2xvZ2luIn0="
# }

# print(requests.delete("https://"+platformaddress+':'+dataflowapi_port+'/dataflow-api/topics/5GMETA_1002_CITS_SMALL_68', headers=keycloak.get_header_with_token("5gmeta", "5Gm3t4!")))
# print(requests.delete("https://"+platformaddress+':'+dataflowapi_port+'/dataflow-api/topics/5GMETA_1003_CITS_SMALL_68', headers=keycloak.get_header_with_token("5gmeta", "5Gm3t4!")))

# time.sleep(100000)
# The request returns the generated topic
r = requests.post(url, headers=keycloak.get_header_with_token("5gmeta", "5Gm3t4!"))
if r.status_code != 200:
    print(r.text)
    exit()
topic = r.text

c = AvroConsumer({
    'bootstrap.servers': platformaddress+':' + bootstrap_port,
    'schema.registry.url':'http://'+platformaddress+':' + registry_port, # 'http://192.168.15.44:8081',
    'group.id': 'group1',
    'api.version.request': True,
    'auto.offset.reset': 'earliest'
})

c.subscribe([topic.upper()])
print("Subscibed to topic: " + str(topic))
print("Running...")

i = 0

while True:
    msg = c.poll(1.0)

    if msg is None:
        #print("Empty msg: " + str(msg) );
        print(".",  end="", flush=True)
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    
    # The AVRO Message here in mydata
    mydata = msg.value() # .decode('latin-1') #.replace("'", '"')

    # The QPID proton message: this is the message sent from the S&D to the MEC
    raw_sd = mydata['BYTES_PAYLOAD']
    msg_sd = proton.Message()
    proton.Message.decode(msg_sd, raw_sd)

    # The msg_sd.body contains the data of the sendor
    # print(msg_sd.body)
    print("Size " + str(sys.getsizeof(msg_sd.body)))

    print(msg_sd.properties)
    print(msg_sd.body)
 

c.close()
