import paho.mqtt.client as paho
import json, time

# device credentials
device_id        = 'pi-server'      # * set your device id (will be the MQTT client username)
# device_secret    = '<DEVICE_SECRET>'  # * set your device secret (will be the MQTT client password)
random_client_id = 'pi-server'      # * set a random client_id (max 23 char)

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
    # check the status property value
    # print(json_data)

    receivedData = json.loads(json_data)
    print "Maximum value: ", receivedData["max_value"]
    # value = json.loads(json_data)['properties'][0]['value']
    # print(json_data["index"])
    # confirm changes to Leylan
    # client.publish(out_topic, json_data)


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
