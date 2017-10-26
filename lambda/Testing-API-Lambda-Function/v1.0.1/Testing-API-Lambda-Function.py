from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import time

from botocore.exceptions import ClientError
client1 = boto3.client('dynamodb')


#This file development is progressed since 13-October 2017
#This is Integration between Device1-Lambda and platform_for_testing functions
#What's Changed: Payload Syntax will change
#What's Pending:
# 2.Try to use 'ValidationException' to check for blank Values
# 3.Try to generate HTTP Status Responses from Lambda Function


'''
CREATE Request:
{
  "operation": "create",
  "tableName": "Cavinkare-Perundurai-Table",
  "payload": [
    {
      "Item": {
        "DeviceId": "Cavinkare-Perundurai",
        "DateTime": "2017-09-27 15:40",
        "Milk Temperature": "3.1",
        "Battery Temperature": "-6.5",
        "AC Voltage": "236",
        "Battery Voltage": "28"
      }
    },
    {
      "Item": {
        "DeviceId": "Cavinkare-Perundurai",
        "DateTime": "2017-09-27 15:41",
        "Milk Temperature": "3.1",
        "Battery Temperature": "-6.5",
        "AC Voltage": "236",
        "Battery Voltage": "28"
      }
    }
  ]
}


READ Request:
{
  	"operation": "read",
  	"tableName": "Cavinkare-Perundurai-Table",
  	"payload": [
    	{
     	 "Key": {
        			"DeviceId": "Cavinkare-Perundurai",
        			"DateTime": "2017-09-27 15:38"
      		}
    	}]
}

'''


def create_Table_In_DynamoDB(passed_tableName):
    print("passed_tableName in create_Table_In_DynamoDB:\n{}".format(passed_tableName))
    response = client1.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'DeviceId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'DateTime',
                'AttributeType': 'S'
            },
        ],
        TableName= passed_tableName,
        KeySchema=[
            {
                'AttributeName': 'DeviceId',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'DateTime',
                'KeyType': 'RANGE'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        StreamSpecification={
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        }
    )
    return response
    #create_Table_In_DynamoDB ends here



def update_Item_in_DynamoDB_Table(passed_event, passed_tableName):
    print("\nupdate_Item_in_DynamoDB passed tableName:\n{}".format(passed_tableName))
    print("\nupdate_Item_in_DynamoDB passed_event:\n{}".format(passed_event))
    #This is to update Milk Temperature if DateTime from incoming source and existing Data Table are the same
    passed_event = json.loads(passed_event)
    response = client1.update_item(
	TableName= passed_tableName,
    Key={
        'DeviceId': {
            'S': passed_event['DeviceId'],
        },
        'DateTime':{
            'S':passed_event['DateTime'],
        }
    },
    ReturnValues='ALL_NEW',
    ReturnConsumedCapacity='TOTAL',
    ReturnItemCollectionMetrics='SIZE',
    UpdateExpression='SET #old_mt = :new_mt, #old_bt = :new_bt, #old_ac = :new_ac, #old_bv = :new_bv',
    ExpressionAttributeNames={
        '#old_mt': 'Milk Temperature',
        '#old_bt': 'Battery Temperature',
        '#old_ac': 'AC Voltage',
        '#old_bv': 'Battery Voltage'
    },
    ExpressionAttributeValues={
        ':new_mt': {
            'S': passed_event['Milk Temperature'],
        },
        ':new_bt': {
            'S': passed_event['Battery Temperature'],
        },
        ':new_ac': {
            'S': passed_event['AC Voltage'],
        },
        ':new_bv': {
            'S': passed_event['Battery Voltage'],
        }
    }
    )
    return response
    #update_Item_in_DynamoDB_Table ends here


def confirmData(incoming_value, existing_value):
    #incoming_value: Value received from External_event
    #existing_value: Value received from DynamoDB_event
    print("Confirming Data between {} and {} ".format(incoming_value, existing_value))
    if (incoming_value == '-' and existing_value == '-'):
        # if incoming_value is - and existing_value is -
        print("Incoming Value is - and Existing Value is -. Will return existing_value {}".format(existing_value))
        return existing_value
    elif incoming_value != '-' and existing_value == '-':
        # if incoming_value is value and existing value is -
        print("Existing Value is -. Hence, returning incoming_value {}".format(incoming_value))
        return incoming_value
    elif incoming_value == '-' and existing_value != '-':
        # if incoming_value is - and existing_value is value
        print("Incoming Value is -. Hence, returning existing_value {}".format(existing_value))
        return existing_value
    else:
        #This is hit when External_event has value and DynamoDB_event also has value
        print("No Value is -. Hence, returning incoming_value {}".format(incoming_value))
        return incoming_value
    #confirmData ends here

def handling_duplicate_entries(outside_event, event_from_DynamoDB, i):
    confirmed_Data = {}
    #We will confirm which values are cogent & which are '-' ,& replace values accordingly
    #Mapping parameters received from outside_event
    outside_event_DeviceId = outside_event['DeviceId']
    outside_event_DateTime = outside_event['DateTime']
    outside_event_mt = outside_event['Milk Temperature']
    outside_event_bt = outside_event['Battery Temperature']
    outside_event_ac = outside_event['AC Voltage']
    outside_event_bv = outside_event['Battery Voltage']

    #Mapping parameters received from DynamoDB_event
    event_from_DynamoDB_DeviceId = event_from_DynamoDB['Item']['DeviceId']
    event_from_DynamoDB_DateTime = event_from_DynamoDB['Item']['DateTime']
    event_from_DynamoDB_mt = event_from_DynamoDB['Item']['Milk Temperature']
    event_from_DynamoDB_bt = event_from_DynamoDB['Item']['Battery Temperature']
    event_from_DynamoDB_ac = event_from_DynamoDB['Item']['AC Voltage']
    event_from_DynamoDB_bv = event_from_DynamoDB['Item']['Battery Voltage']

    #Confirming Data between both events
    confirmed_Data['DeviceId'] = confirmData(outside_event_DeviceId, event_from_DynamoDB_DeviceId)
    confirmed_Data['DateTime'] = confirmData(outside_event_DateTime, event_from_DynamoDB_DateTime)
    confirmed_Data['Milk Temperature'] = confirmData(outside_event_mt, event_from_DynamoDB_mt)
    confirmed_Data['Battery Temperature'] = confirmData(outside_event_bt, event_from_DynamoDB_bt)
    confirmed_Data['AC Voltage'] = confirmData(outside_event_ac, event_from_DynamoDB_ac)
    confirmed_Data['Battery Voltage'] = confirmData(outside_event_bv, event_from_DynamoDB_bv)

    #Dumping confirmed data in a json file
    confirmed_Data = json.dumps(confirmed_Data)
    print("\nConfirmed Data after handling_duplicate_entries:\n{}".format(confirmed_Data))
    return confirmed_Data
    #handling_duplicate_entries ends here

def tableName_Checker(received_string):
    str = received_string
    #length_of_string = len(str)
    cursor_index = str.find("-Table", 1)
    if cursor_index != -1:
        #'-Table' string exists in Table Name
        DeviceId = str[0:cursor_index]
        return DeviceId
    else:
        #'-Table' string does not exist in Table Name
        return -1


def handler(event, context):
    #main src function
    print("Received Event:\n{}".format(event))
    DeviceId_received = tableName_Checker(event['tableName'])
    print("DeviceId_received from tableName_Checker is:\t{}\n".format(DeviceId_received))
    if DeviceId_received == -1:
        # -1 is obtained when tableName does not consists a '-Table' string
        return "Incorrect tableName"
    response_to_sent = {}
    dynamo = boto3.resource('dynamodb').Table(event['tableName'])
    operation = event['operation']
    operations = {
        'create': lambda x: dynamo.put_item(**x),
        'read': lambda x: dynamo.get_item(**x),
        'update': lambda x: dynamo.update_item(**x)
    }

    if event['operation'] == 'create':
        for i in range(0,len(event['payload'])):
            # for loop runs from 0 to number of items in payload
            print("Loop Number:\t{}".format(i))
            if DeviceId_received != event['payload'][i]['Item']['DeviceId'] :
                # Returned DeviceId from 'tableName_Checker()' does not match DeviceId in received_event[i]
                # This also handles if DeviceId is null or not null problem
                response_to_sent[i] = "Incorrect DeviceId"
            elif (event['payload'][i]['Item']['DateTime'] == "") or (event['payload'][i]['Item']['DateTime'] == " "):
                # This handles if DateTime is null or not null problem
                response_to_sent[i] = "Incorrect DateTime"
            else:
                #Create a 'read' operation internally to check if reading exists or not before 'create' operation
                a = {
                    "operation": "read",
                    "tableName": event['tableName'],
                    "payload": [
                    {
                        "Key":
                        {
                            "DeviceId": event['payload'][i]['Item']['DeviceId'],
                            "DateTime": event['payload'][i]['Item']['DateTime']
                        }
                    }
                    ]
                }
                try:
                    #This below statement has to stay as "a['payload'][0]" as it is for the above declared 'read' request
                    response = operations['read'](a['payload'][0])
                    print("Response from Initial Read Operation:\n{}".format(response))
                    if 'Item' not in response:
                        print("\nTable exists. But Value does not exist\n")
                        response = operations['create'](event['payload'][i])
                        print("Response Obtained after Creating New Value:\n{}".format(response))
                        response_to_sent[i] =  "Added New Entry" #set_confirmation['ResponseMetadata']
                    else:
                        #Table is found. Item is found
                        print("\nTable is found. Item is found. Must Update Item now\n")
                        final_payload_to_update = handling_duplicate_entries(event['payload'][i]['Item'], response, i)
                        response = update_Item_in_DynamoDB_Table(final_payload_to_update, event['tableName'])
                        #response = operations['update'](final_payload_to_update)
                        print("\nResponse obtained after Updating existing value:\n{}".format(response))
                        response_to_sent[i] = "Updated Entry" #set_confirmation['ResponseMetadata']
                except ClientError as r:
                    if r.response['Error']['Code'] == 'ResourceNotFoundException':
                        print("Table Does not Exist")
                        response = create_Table_In_DynamoDB(event['tableName'])
                        print("Response Obtained after Creating New Table:\n{}".format(response))
                        time.sleep(10)
                        response = operations['create'](event['payload'][i])
                        print("Response obtained after Adding New Entry:\n{}".format(response))
                        response_to_sent[i] =  "Added New Entry" #set_confirmation['ResponseMetadata']
                    elif r.response['Error']['Code'] == 'ValidationException':
                        print("\nValidationException caught. One or more values are received as blank\n")
        print("Sending this response:\n{}\n".format(response_to_sent))
        response_to_sent = json.dumps(response_to_sent)
        print("\nThis is the response to sent:\n{}".format(response_to_sent))
        return response_to_sent

    elif event['operation'] == 'read':
        try:
            response = operations['read'](event['payload'][0])
            if 'Item' not in response:
                #Table exists but value does not exists
                response_to_sent[0] =  "Value not Found" #set_confirmation['ResponseMetadata']
                response_to_sent = json.dumps(response_to_sent)
                print("\nThis is the response to sent:\n{}".format(response_to_sent))
                return response_to_sent
            else:
                #Table is found. Item is found
                response_to_sent[0] = response['Item']
                response_to_sent = json.dumps(response_to_sent)
                print("\nThis is the response to sent:\n{}".format(response_to_sent))
                return response_to_sent
        except ClientError as r:
            if r.response['Error']['Code'] == 'ResourceNotFoundException':
                response_to_sent[0] = "Table Not Found"
                response_to_sent = json.dumps(response_to_sent)
                print("\nThis is the response to sent:\n{}".format(response_to_sent))
                return response_to_sent
    else:
        response_to_sent[0] = "Incorrect Operation Type"
        response_to_sent = json.dumps(response_to_sent)
        print("\nThis is the response to sent:\n{}".format(response_to_sent))
        return response_to_sent
