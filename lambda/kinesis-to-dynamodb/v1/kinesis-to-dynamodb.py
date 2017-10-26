from __future__ import print_function

import boto3
import base64
import json

print('Loading function')
dynamo = boto3.resource('dynamodb').Table('IoT_Table')



'''
This is a testing purpose function for inserting incoming data from aws iot to aws dynamoDB
This Lambda function is triggered, when, kinesis stream named 'stream-for-iot' receives latest data
This kinesis stream is triggered, when, aws iot rule named 'MyKinesisRule' receives latest entry from device by running SQL statement: "SELECT * FROM '/sbs/devicedata/#'"
Code for posting data to aws iot under that topic is downloaded from : "https://github.com/awslabs/sbs-iot-data-generator/blob/master/sbs.py"

This function's working is as follows:
1. Read data from 'Kinesis Stream'
2. Decode the 'payload' from the incoming kinesis stream
3. Convert that 'payload' to 'Item'-based payload for inserting it into DynamoDB
4. Insert the Record in DynamoDB in individual columns

'''

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    operations = {
        'create': lambda x: dynamo.put_item(**x),
        'read': lambda x: dynamo.get_item(**x),
        'update': lambda x: dynamo.update_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
        'list': lambda x: dynamo.scan(**x),
        'echo': lambda x: x,
        'ping': lambda x: 'pong'
    }
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])
        print("Decoded payload: " + payload)
        payload = json.loads(payload)
        print("Payload Loaded in json format is:\n")
        print(payload)
        print(payload['deviceId'])

        a = {
            "stack": [
                {
                    "Item":
                        {
                            "DeviceId": payload['deviceId'],
                            "DateTime": payload['dateTime'],
                            "Parameter": payload['deviceParameter'],
                            "Value": payload['deviceValue'],
                        }
                }
            ]
        }
        print(a['stack'][0])

        response = operations['create'](a['stack'][0])
        return response

    '''
    This is the type of received payload from kinesis stream
    {"deviceParameter": "Sound", "deviceValue": 106, "deviceId": "SBS05", "dateTime": "2017-10-26 12:34:42"}
    '''

    #return 'Successfully processed {} records.'.format(len(event['Records']))
