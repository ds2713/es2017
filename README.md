# EE3-24 Embedded Systems Spring Term 2017
_Embedded Systems Coursework Folder_
## 1. IOT Sensor Project

We're using the EPS8266 microcontroller with Micropython. This is connected to the ADS1115 ADC reading values from a SM-24 geophone (seismic data).

You will need `ampy` (`sudo pip install ampy`) on your computer to upload files to the microcontroller, and `screen` (`PuTTY` for you heathens) for serial communications.

### Functionality and Processing Information
1. ADC configured to read data from sensor. ES8266 configured to read data from ADC.

2. ESP8266 will query a server for the setup time data. This assumes that a suitable server is running the time_server.py script which is included.

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

10. There used to be a timeout which raises an annoying exception and is hard to fix without a reset. Running `connect()` and `disconnect()` before and after each message prevents this timeout. The device runs easily overnight, up to, and above shock index numbers of 500.
  * The only concern now is an overflow, which is unlikely (assuming signed 32-bit integer).

11. The "real units" of the seismograph are measured in Volts per metres per second. In other words, the device measures velocity. However, the specific velocity is not needed in our detections for shocks, which is why we have not gone into interpretting the voltage data specifically. Additionally, the transfer function between the voltage and m/s varies with frequency (the datasheet has a Bode plot). 

12. Website building has begun. 

### Remaing possibilities
1. The website inside the `/docs` folder needs to be made. Active display of data?

2. SSL connection for the messages to be encrypted.

3. Server-side calculations? Aka additional data processing that is too intensive for the poor little microcontroller.

4. Additional features, such as buying buzzer. Battery? Light sensor for intrusion detection. Noise floor threshold?

5. Analogue filtering.
