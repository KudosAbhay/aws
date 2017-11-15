from __future__ import print_function

import boto3
import json
import logging
import os
import time
import uuid

# Version Number: v1.0.0
# Creation Date: 15-November-2017
# Updation Date: 15-November-2017

'''
Sample Request used to hit:
{
  "text": "Hello There"
}
'''
def response_parser(passed_Status_Code, passed_response):
    response_to_sent = json.dumps(passed_response)
    response_to_sent = json.loads(response_to_sent)
    return {'statusCode': passed_Status_Code,
            'body': response_to_sent,
            'headers': {'Content-Type': 'application/json'}}

def handler(event, context):
    dynamo = boto3.resource('dynamodb').Table('Trial-Table')
    timestamp = int(time.time() * 1000)
    item = {
        'DeviceId': str(uuid.uuid1()),
        'text': event['text'],
        'checked': False,
        'DateTime': str(timestamp),
        'updatedAt': timestamp,
    }
    dynamo.put_item(Item=item)
    return response_parser(201, 'Entry Added')
