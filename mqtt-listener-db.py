import paho.mqtt.client as paho
import json, time
import elasticsearch
import datetime

# connect to the ES database
# es object has to be seen in all methods hence here
es = elasticsearch.Elasticsearch()

# device credentials
device_id        = 'db-server'      # * set your device id (will be the MQTT client username)
# device_secret    = '<DEVICE_SECRET>'  # * set your device secret (will be the MQTT client password)
random_client_id = 'db-server'      # * set a random client_id (max 23 char)

# connection event
def on_connect(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))

# subscription event
def on_subscribe(client, userdata, mid, gqos):
    print('Subscribed: ' + str(mid))

# received message event
def on_message(client, obj, msg):
    # get the JSON message
    json_data = msg.payload
    receivedData = json.loads(json_data)

    # print for debug
    #print(receivedData)

    # check if message read is sensor event, else don't process
    if type(receivedData) is dict:

        # get device ID from the message, construct name of ES index
        sensor_id = receivedData["device_id"]
        es_index = 'lsd' + str(sensor_id)

        # extract and reformat (into ES format) time of the sensor reading
        sensor_time = receivedData["time"]
        es_time = str(sensor_time[0]) + "-" + str(sensor_time[1]).zfill(2) + "-" + str(sensor_time[2]).zfill(2) + "T" + str(sensor_time[3]) + ":" + str(sensor_time[4]) + ":" + str(sensor_time[5])
        #print (es_time)

        # check type of event - shock or intrusion
        if (receivedData["intrusion"] == 0):
            # SHOCK EVENT
            print("Shock")

            # log event into console
            # print ("Maximum value: ", receivedData["max_value"])
            # value = json.loads(json_data)['properties'][0]['value']
            # print(json_data["index"])
            # confirm changes to Leylan
            # client.publish(out_topic, json_data)

            #construct elasticsearch data
            data = {}
            data['max'] = receivedData["max_value"]
            data['mean'] = receivedData["mean_value"]
            data['min'] = receivedData["min_value"]
            data['time'] = es_time

            #print for debug
            #print (data)

            # post to elasticsearch index
            es.index(index=es_index, doc_type='shock', body=data)
        else:
            #INTRUSION EVENT
            print("Intrusion")
            # construct data
            data = {}
            data['time'] = es_time
            data['intensity'] = receivedData["intensity"]

            # print for debug
            #print(data)

            # post to elasticsearch index
            es.index(index=es_index, doc_type='intrusion', body=data)


def main():

    # ------------- #
    # MQTT settings #
    # ------------- #

    # create the MQTT client
    client = paho.Client(client_id=random_client_id, protocol=paho.MQTTv31)  # * set a random string (max 23 chars)

    # assign event callbacks
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe


    # device topics
    in_topic  = '/esys/mdma'  # receiving messages
    out_topic = '/esys/mdma'  # publishing messages

    # client connection
    # client.username_pw_set(device_id, device_secret)  # MQTT server credentials
    client.connect("192.168.0.10")                   # MQTT server address
    client.subscribe(in_topic, 0)                     # MQTT subscribtion (with QoS level 0)

    rc = 0
    while rc == 0:
        rc = client.loop()

    print('rc: ' + str(rc))

if __name__ == "__main__":
    main()
