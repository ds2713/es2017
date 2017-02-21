# EE3-24 Embedded Systems Spring Term 2017
_Embedded Systems Coursework Repository_
# IOT Sensor Project - LSD: Lightweight Shock Detection
## Group - MDMA: Martin David Meng Association

We're using the EPS8266 microcontroller with Micropython. This is connected to the ADS1115 ADC reading values from a SM-24 geophone (seismic data).

You will need `ampy` (`sudo pip install ampy`) on your computer to upload files to the microcontroller, and `screen` (`PuTTY` for you heathens) for serial communications.

## Descriptions of Files

### `adc_driver/`
This folder contains the Micropython driver for the Analogue-to-Digital Converter (ADC), which we used to interface with the ADS1115.

### `Pictures and Data/`
A folder containing some pictures of the longevity of the LSD. They are screencaps of the device's output after several days of continuous successful operation.

### `website/`
The website for LSD can be found by opening the `index.html` file in the `website` folder in our repository. It was created using an online editor [Silex editor] (https://www.silex.me/) and some subsequent edits were done manually. It describes the use-case of the product, gives some background information on the team, and there is a demo sub-page. If the website is run on the same machine as the Elasticsearch database, the demo shows real data from the database. In the code submitted, this is replaced by a static picture to illustrate how the consumer-side of the data processing looks like.

### `mqtt-listener-db.py`
Script to be run on our server. Subscribes to the MQTT topic to which the LSD posts, reads messages, reformats them to a format readable by Elasticsearch, and inserts data into the Elasticsearch index. Connects to the default Elasticsearch index, running on the localhost (in reality, both database and this script would always be running on the same machine). It distinguishes between the types of messages posted by LSD and only indexes the relevant ones.
#### Dependencies
[Elasticsearch and Kibana] (https://www.elastic.co/downloads) running on localhost, Elasticsearch mapping (definition of data type which will be inserted) exists in the index (database).

### `time-server.py`
This is a server that needs to be run on the same network as the LSD. Its IP address will need to be manually configured inside the LSD. The script sets up a server that will return the current time in text when an HTTP request is sent. This time can be parsed by whatever devices need the time.

### `main.py`
This is the main file of our LSD. The operation and its features are described below.

#### `http_get(url, port)`
This function takes in a URL and a port number before returning the resulting HTTP response. This is used in the `main()` function to obtain the time from the server runing `time-server.py`.

#### `send_mqtt(the_message)`
This function takes in a message in text, converts it to JSON. It then takes the globally declared `client` object, attempts to connect. It then attempts to empty the globally declared `message_cache` which stores unsent messages. After the cache is emptied, it will send the current message. If this is not possible, the current message is put into the cache, for the subsequent attempts.

If the connection is succesful and all messages are sent out, the client is disconnected. This was discovered to be necessary to prevent a timeout error from occuring in certain cases.

#### `main()`
##### Setup
LSD first attempts to connects to a network. Then creates and configures the global MQTT object used for all messages. The ADC is then configured, followed by two output pinns: LED and a PWM. The PWM is set at a 0% duty cycle because changing duty cycle to and from 0% is faster than initialising and deinitialising the PWM output. Then, the time is configured by querying the server. If this fails, it defaults to midnight on Jan 1, 2017.

##### Main Operation
Three values of three pins are read. The Pin(2) corresponds to the LDR. It is configured to show higher readings with more light. If this reading exceeds 1000, this means the box is opened. If this is the case, LSD sends a message notifying the server of this intrusion. The message also contains the light intensity, the time, and the device's unique ID.

Pin(0) is the potentiometer used to calibrate the sensitivity of the shock detection. Pin(3) reads from the seismograph. These are compared. If there is no shock detected, the reading from Pin(3) is stored in a circular "historic" buffer. Then the loop repeats indefinitely, taking readings.

If there is a shock detected, a number events happen.
1. Buzzer goes off by raising the duty cycle to 50%. LED goes on!
2. Time is recorded.
3. The subsequent readings are taken, and stored in the output buffer. The buzzer goes off.
4. The historic buffer is added to the output buffer.
5. Statistics are taken, and a message is created and sent. The message contains the device ID, the index number of the shock, the time, the maximum, the minimum, and the mean values.
6. The buffers are cleared, the LED turned off, and the index incremented.

#### Features
1. The "real units" of the seismograph are measured in Volts per metres per second. In other words, the device measures velocity. However, the specific velocity is not needed in our detections for shocks, which is why we have not gone into interpretting the voltage data specifically. Additionally, the transfer function between the voltage and m/s varies with frequency (the datasheet has a Bode plot).

2. A cache system for the messages when an MQTT message is sent. If this does not work, the message is stored. Next time a message needs to be sent, the cache will be emptied first (send first item, delete, repeat until empty). Then, the current message is sent.

10. The device runs easily overnight, up to, and above shock index numbers of 500. The only concern now is an overflow, which is unlikely (assuming signed 32-bit integer). Also, over a thousand damaging shocks to a device is (hopefully) unlikely.

4. Functions without any issues from a power bank!
