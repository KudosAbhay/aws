'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
'''

# First Created: 13-11-2017
# Last Updated: 15-11-2017
#
# Workflow:
# 1. Thing publishes payload under the specified format on topic: '../shadow/update/'
# 2. Device Shadow is updated accordingly on aws iot accordingly
# 3. Subscribe to the topic: '../shadow/update/accepted' from aws iot cloud through 'test' option
# 4. Send payload for any changes to be made under 'desired' key in json on this topic
# 5. Thing receives this new update as it is listening to the same topic
# 6. Once this thing receives a new payload, it decodes the values and acts accordingly
#
# What's changed?
# 1. Device can now decode specified value from the incoming payload
#

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import datetime
import random
import json

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("--------------\n\n")
    if 'desired' in message.payload:
        print("Received a new message: ")
        print(message.payload)
        a = str(message.payload)
        a = json.loads(message.payload)
        print(a['state']['desired']['set_temp'])
    else:
        print("nothing new")
    print("--------------\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="$aws/things/Second_Thing/shadow/update", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
topic_to_listen = '$aws/things/Second_Thing/shadow/update/accepted'

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

def create_payload(value):
    # now = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # m_t = str(random.uniform(4.0, 23.9))
    # b_t = str(random.uniform(-6.0, 5.1))
    SendingMessageString = json.dumps(
        {
            "state": {
                "reported": {
                    "set_temp": value,
                    "actual_temp": value
                    }
                }
        }
    )
    return SendingMessageString



# Publish to the same topic in a loop forever
loopCount = 0
while True:
    #Listen for Changes from Cloud
    print("~~~~ First Listener ~~~~")
    myAWSIoTMQTTClient.subscribe(topic_to_listen, 1, customCallback)
    print("Sleeping for 2 seconds")
    time.sleep(2)

    #Send Payload of Data from Device
    print("~~~~ Publisher ~~~~")
    payload_to_send = create_payload(32.5)
    myAWSIoTMQTTClient.publish(topic, payload_to_send, 1)
    print("Sleeping for 15 seconds")
    time.sleep(15)

    #Listen for Changes again
    print("~~~~ Last Listener ~~~~")
    myAWSIoTMQTTClient.subscribe(topic_to_listen, 1, customCallback)
    print("Sleeping for 2 seconds")
    time.sleep(2)
    loopCount += 1
