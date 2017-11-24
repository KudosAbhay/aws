import paho.mqtt.client as mqtt #import the client1
import ssl, time, sys, json
import RPi.GPIO as GPIO
import argparse

########################################
# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-t", "--thing", action="store", required=True, dest="thingName", help="Your AWS IoT Thing Name")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")

# =======================================================
args = parser.parse_args()
MQTT_HOST = args.host
CA_ROOT_CERT_FILE = args.rootCAPath
THING_NAME = args.thingName
THING_CERT_FILE = args.certificatePath
THING_PRIVATE_KEY_FILE = args.privateKeyPath
RESPONSE_RECEIVED = False
LED_PIN = 14
MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 45

SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
SHADOW_UPDATE_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/accepted"
SHADOW_UPDATE_REJECTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/rejected"
SHADOW_UPDATE_DELTA_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/delta"

SHADOW_STATE_DOC_INITIAL = """{"state" : {"desired" : {"LED" : "OFF"}, "reported" : {"LED" : "OFF"}}}"""
SHADOW_STATE_DOC_LED_ON = """{"state" : {"reported" : {"LED" : "ON"}}}"""
SHADOW_STATE_DOC_LED_OFF = """{"state" : {"reported" : {"LED" : "OFF"}}}"""

change_of_state = ""
########################################
# Master Function where changes will actually take place
def LED_Status_Change(Shadow_State_Doc, Type):
    # print "\nParsing Shadow Json..."
    DESIRED_LED_STATUS = ""
    SHADOW_State_Doc = json.loads(Shadow_State_Doc)
    # print SHADOW_State_Doc
    DESIRED_LED_STATUS = SHADOW_State_Doc['state']['LED']
    if DESIRED_LED_STATUS == "ON":
        # Turn LED ON
        print "\nTurning ON LED..."
        GPIO.output(LED_PIN, GPIO.HIGH)
        client.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_LED_ON,qos=1)
    elif DESIRED_LED_STATUS == "OFF":
        # Turn LED OFF
        print "\nTurning OFF LED..."
        GPIO.output(LED_PIN, GPIO.LOW)
        client.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_LED_OFF,qos=1)
    else:
        print "---ERROR--- Invalid LED STATUS."
    global change_of_state
    change_of_state = DESIRED_LED_STATUS

########################################
# This function will be invoked every time, whenever a new message arrives for the subscribed topic
def on_message(mosq, obj, msg):
	if str(msg.topic) == SHADOW_UPDATE_DELTA_TOPIC:
		print "\nNew Delta Message Received..."
		SHADOW_STATE_DELTA = str(msg.payload)
		print SHADOW_STATE_DELTA #print message received
		LED_Status_Change(SHADOW_STATE_DELTA, "DELTA")
	elif str(msg.topic) == SHADOW_UPDATE_ACCEPTED_TOPIC:
		print "\nupdated Accepted Acknowledgement received from AWS.."
	elif str(msg.topic) == SHADOW_UPDATE_REJECTED_TOPIC:
		SHADOW_UPDATE_ERROR = str(msg.payload)
		print "\n---ERROR--- \nFailed to Update the Shadow...\nError Response: " + SHADOW_UPDATE_ERROR


########################################
def on_connect(Client, userdate, flag, rc):
    if rc == 0:
        print("CONNECTED TO AWS IoT SUCCESSFULLY")
    elif rc == 1:
        print("incorrect protocol version")
    elif rc == 2:
        print("Invalid Client identifier while connecting")
    elif rc == 3:
        print("Server unavailable")
    elif rc == 4:
        print("Bad Username or password")
    elif rc == 5:
        print("Connection not authorised")

########################################
def on_publish(mosq, obj, mid):
    print("PUBLISHED SUCCESSFULLY")

########################################
def on_subscribe(mosq, obj, mid, granted_qos):
    print("SUBSCRIBED SUCCESSFULLY")

########################################
def on_log(mosq, obj, level, string):
    print("log:", string)

########################################


########################################
# Initiate GPIO for LED
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
########################################

print("Initiating MQTT Client..")
client = mqtt.Client(THING_NAME) #create new instance

# Configure TLS Set
client.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, keyfile=THING_PRIVATE_KEY_FILE, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

########################################
#attach callback functions for client
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
########################################

print("connecting to AWS IoT...")
client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
time.sleep(10) #wait
print("creating shadow..")
client.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_INITIAL,qos=1)

count = 1
while True:
    client.loop_start() #start the loop
    print "Loop Number:\t"+str(count)
    #Subscribe to Topics
    client.subscribe(SHADOW_UPDATE_ACCEPTED_TOPIC, 1)
    client.subscribe(SHADOW_UPDATE_REJECTED_TOPIC, 1)
    client.subscribe(SHADOW_UPDATE_DELTA_TOPIC, 1)
    time.sleep(20) # wait
    #Publish messages on Topic depending on the accepted value for LED on cloud
    if change_of_state == "ON":
        client.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_LED_ON,qos=1)
    elif change_of_state == "OFF":
        client.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_LED_OFF,qos=1)
    client.loop_stop() #stop the loop
    count = count + 1
