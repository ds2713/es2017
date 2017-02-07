# EE3-24 Embedded Systems Spring Term 2017
_Embedded Systems Coursework Folder_
## 1. IOT Sensor Project

We're using the EPS8266 microcontroller with Micropython. This is connected to the ADS1115 ADC reading values from a SM-24 geophone (seismic data).

You will need `ampy` (`sudo pip install ampy`) on your computer to upload files to the microcontroller, and `screen` (`PuTTY` for you heathens) for serial communications.

### Functionality and Processing Information
1. ADC configured to read data from sensor. ES8266 configured to read data from ADC.

2. Readings stored in historic (circular) buffer.

3. When a shock exceeds a threshold, the output buffer is filled with the subsequent readings, and with the historic readings.

4. A buzzer sounds, and an LED lights up. Buzzer stays on until subsequent readings are taken. The LED remains on until after the sending of the message.

5. The time of the shock, the maximum value, the  minimum value, and the index number of the shock are recorded.

6. This is put into `JSON` format.

7. Successfully sends this to the MQTT broker.

8. Historic buffer is cleared, entire process repeats itself.

9. A cache system. MQTT message is sent. If this does not work, the message is stored. Next time a message needs to be sent, the cache will be emptied first (send first item, delete, repeat until empty). Then the current message sent. Two caveats:
  * Assumes successful connection will happen before memory runs out. Otherwise crashes.
  * There is no attempt to check the network connection or reestablish it if it decides to fail.

  In other words, the cache system works exclusively for the problem of the broker temporarily going offline.

### Remaing possibilities
1. The website inside the `/docs` folder needs to be made. Active display of data?

2. SSL connection for the messages to be encrypted.

3. Server-side calculations? Aka additional data processing that is too intensive for the poor little microcontroller.

4. Time needs to be set via the network.

5. Network access? The internal network lacks internet access atm. This makes it difficult for time. Also, what about transmission to another server for recording?

6. Additional features, such as buying buzzer. Battery? Light sensor for intrusion detection. Noise floor threshold?

7. Units and real values of the sensor data.

8. Analogue filtering.

9. Some kind of network repeating thing (in progress). Must be durable for long term use.

### Talk to Dr. Stott about:

1. Time data on the network. Is there a way to internet?

2. Server functions. Do we implement stuff for his Pi? For our own server? Can we set up a local listener and direct the data to local database for display on the website?

3. Triggering, statistics, processing. What constitutes sufficient of each?

4. SSL stuff.

5. What is cloud functionality?
