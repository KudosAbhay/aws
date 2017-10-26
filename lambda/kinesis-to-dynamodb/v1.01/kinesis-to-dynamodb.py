from __future__ import print_function

import boto3
import base64
import json

print('Loading function')
dynamo = boto3.resource('dynamodb').Table('Shadow-Kinesis-Lambda-DynamoDB')


'''Usage:
(This is done for Our Sample Data)
->AWS IoT Device Shadow Update
    -> Data passed to kinesis using AWS IoT Rule
        -> Lambda Function Triggered on kinesis-stream receiving latest entry
            -> Write entry to dynamoDB table

Complete Code Usage is inspired from this blog: 'https://aws.amazon.com/blogs/big-data/build-a-visualization-and-monitoring-dashboard-for-iot-data-with-amazon-kinesis-analytics-and-amazon-quicksight/'

Flow of working:
This Lambda function is triggered, when, kinesis stream named 'stream-for-iot' receives latest data
This kinesis stream is triggered, when, aws iot rule named 'MyKinesisRule' receives latest entry from device by running SQL statement: 'SELECT * FROM '$aws/things/RaspberryPi/shadow/update'
Code for posting data to aws iot under that topic is downloaded from : 'https://github.com/awslabs/sbs-iot-data-generator/blob/master/sbs.py'

This function's overall working is as follows:
1. Read data from 'Kinesis Stream'
2. Decode the 'payload' from the incoming kinesis stream
3. Convert that 'payload' to 'Item'-based payload for inserting it into DynamoDB
4. Insert the Record in DynamoDB in respective columns

Core working of this function:
1.  DynamoDB is connected for table named: 'Shadow-Kinesis-Lambda-DynamoDB'
2.  'operations' are declared w.r.t DynamoDB (i.e. Create / Read / Update)
3.  Sample received event from kinesis-stream is: {'Records': [{'kinesis': {'kinesisSchemaVersion': '1.0', 'partitionKey': 'a7888142-913f-4fa1-bfdc-1d4d8539b3e9', 'sequenceNumber': '49577900309035271759973689251927765313653637004002328578', 'data': 'eyJzdGF0ZSI6IHsiZGVzaXJlZCI6IHsiQmF0dGVyeSBUZW1wZXJhdHVyZSI6IDAsICJNaWxrIFRlbXBlcmF0dXJlIjogMTksICJEZXZpY2VJZCI6ICJEZXZpY2UzIiwgIkRhdGVUaW1lIjogIjIwMTctMTAtMjYgMTU6NTE6NTIifSwgInJlcG9ydGVkIjogeyJJdGVtIjogeyJCYXR0ZXJ5IFRlbXBlcmF0dXJlIjogMCwgIk1pbGsgVGVtcGVyYXR1cmUiOiAxOSwgIkRldmljZUlkIjogIkRldmljZTMiLCAiRGF0ZVRpbWUiOiAiMjAxNy0xMC0yNiAxNTo1MTo1MiJ9fX19', 'approximateArrivalTimestamp': 1509013312.285}, 'eventSource': 'aws:kinesis', 'eventVersion': '1.0', 'eventID': 'shardId-000000000000:49577900309035271759973689251927765313653637004002328578', 'eventName': 'aws:kinesis:record', 'invokeIdentityArn': 'arn:aws:iam::461024261025:role/admin-role', 'awsRegion': 'ap-southeast-1', 'eventSourceARN': 'arn:aws:kinesis:ap-southeast-1:461024261025:stream/stream-for-iot'}]}
4.  Incoming Stream record from kinesis is decoded and loaded in json format
4.  Values from this json are loaded in 'Item'-oriented json payload for inserting in DynamoDB
5.  This new payload formed is inserted in DynamoDB table (which is mentioned in first point)
'''

def handler(event, context):
    print("Received kinesis event: ")
    print(event)

    operations = {
        'create': lambda x: dynamo.put_item(**x),
        'read': lambda x: dynamo.get_item(**x),
        'update': lambda x: dynamo.update_item(**x),
    }

    for record in event['Records']:
        #Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])

        #Load the 'payload' in json format
        payload = json.loads(payload)
        print("Decoded payload:\n")
        print(payload)
        print("\n")

        dynamoDB_payload = {
            "stack": [
                {
                    "Item":
                        {
                            "DeviceId": payload['state']['reported']['Item']['DeviceId'],
                            "DateTime": payload['state']['reported']['Item']['DateTime'],
                            "Battery Temperature": payload['state']['reported']['Item']['Battery Temperature'],
                            "Milk Temperature": payload['state']['reported']['Item']['Milk Temperature']
                        }
                }
            ]
        }

        #print 0th Item from the 'a' payload to check, if values are parsed in from kinesis stream
        print(dynamoDB_payload['stack'][0])

        response = operations['create'](dynamoDB_payload['stack'][0])
        print(response)
    return response
    #return 'Successfully processed {} records.'.format(len(event['Records']))
