from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

def publish_to_sns(message):
    #Send an SMS if an error occurs or an Exception is hit
    sns = boto3.client('sns')
    return sns.publish(
        TopicArn='arn:aws:sns:ap-southeast-1:<ACCOUNT ID>:MyTopic',
        Message=json.dumps(message),
        MessageStructure='string',
        MessageAttributes={
            'summary': {
                'StringValue': 'Summary String Here',
                'DataType': 'String'
                }
          }
    )


def handler(event, context):
    a = publish_to_sns('Hello from Lambda Function written in Python')
    if(a):
        return "SMS Send Successfully"
    else:
        raise Exception('SMS Failed to Sent')
