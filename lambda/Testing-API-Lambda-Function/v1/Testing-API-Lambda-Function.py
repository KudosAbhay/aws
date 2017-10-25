from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import time

from botocore.exceptions import ClientError

#This file contains customized responses for Client Side
#Creation Date: 09-October-2017
#This is meant to parse multiple payloads received in one json response
#Latest Changes: Increased Timeout from 12 Seconds to 239 seconds

'''
CREATE Request:
{
  "operation": "create",
  "tableName": "Mother-Dairy 1-Table",
  "payload": {
    "Items": [
      {
        "DeviceId": "Mother-Dairy 1",
        "DateTime": "2017-10-08 19:38",
        "Milk Temperature": "24.5",
        "TSS Temperature": "5.5",
        "AC Voltage": "224",
        "Battery Voltage": "18"
      },
      {
        "DeviceId": "Mother-Dairy 1",
        "DateTime": "2017-10-08 19:39",
        "Milk Temperature": "24.5",
        "TSS Temperature": "5.5",
        "AC Voltage": "224",
        "Battery Voltage": "18"
      }
    ]
  }
}


READ Request:
{
  "operation": "read",
  "tableName": "Cavinkare-Perundurai-Table",
  "payload": {
    "Key": {
      "DeviceId": "Cavinkare-Perundurai",
      "DateTime": "2017-09-27 15:37"
    }
  }
}
'''

client1 = boto3.client('dynamodb')

def create_Table_In_DynamoDB(passed_event, passed_tableName):
    print("passed_event in create_Table_In_DynamoDB:\n{}".format(passed_event))
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


def get_Specific_Item_From_DynamoDB_Table(passed_event):
    #This is to read Data from DynamoDB Table
    response = client1.get_item(
        TableName=passed_event['tableName'],
        Key={
            'DeviceId': {
                'S': passed_event['payload']['Key']['DeviceId'],
            },
            'DateTime':{
                'S':passed_event['payload']['Key']['DateTime'],
            }
        },
    ConsistentRead=True,
    ReturnConsumedCapacity='TOTAL',
    )
    return response['Item']
    #get_Specific_Item_From_DynamoDB_Table ends here



def create_Item_In_DynamoDB_Table(passed_event, passed_tableName):
    try:
        print("\nResponse in create_Item_In_DynamoDB_Table passed_event:\n{}".format(passed_event))
        #This is to Create a New Entry in DynamoDB Table
        response = client1.put_item(
        TableName=passed_tableName,
        Item={
            'DeviceId': {
                'S': passed_event['DeviceId'], #['payload']['Items']['DeviceId'],
            },
            'DateTime': {
                'S': passed_event['DateTime'], #['payload']['Items']['DateTime'],
            },
            'Milk Temperature': {
                'S': passed_event['Milk Temperature'], #['payload']['Items']['Milk Temperature'],
            },
            'TSS Temperature': {
                'S': passed_event['TSS Temperature'], #['payload']['Items']['TSS Temperature'],
            },
            'AC Voltage': {
                'S': passed_event['AC Voltage'] #['payload']['Items']['AC Voltage'],
            },
            'Battery Voltage': {
                'S': passed_event['Battery Voltage'] #['payload']['Items']['Battery Voltage'],
            }
        },
        ReturnValues='ALL_OLD',
        ReturnConsumedCapacity='TOTAL',
        ReturnItemCollectionMetrics='SIZE',
        )
        print("create_Item_In_DynamoDB_Table created Item Successfully")
        return response
    except ClientError as r:
        if r.response['Error']['Code'] == 'ResourceNotFoundException':
            return "Creating Table. Please try uploading data after few seconds"
    #create_Item_In_DynamoDB_Table ends here


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
    UpdateExpression='SET #old_mt = :new_mt, #old_tss = :new_tss, #old_ac = :new_ac, #old_bt = :new_bt',
    ExpressionAttributeNames={
        '#old_mt': 'Milk Temperature',
        '#old_tss': 'TSS Temperature',
        '#old_ac': 'AC Voltage',
        '#old_bt': 'Battery Voltage'
    },
    ExpressionAttributeValues={
        ':new_mt': {
            'S': passed_event['Milk Temperature'],
        },
        ':new_tss': {
            'S': passed_event['TSS Temperature'],
        },
        ':new_ac': {
            'S': passed_event['AC Voltage'],
        },
        ':new_bt': {
            'S': passed_event['Battery Voltage'],
        }
    }
    )
    return response
    #update_Item_in_DynamoDB_Table ends here


def get_Latest_Item_From_DynamoDB_Table(received_DeviceId, received_DateTime, received_TableName):
    #This is to read Data from DynamoDB Table
    try:
        response = client1.get_item(
            TableName=received_TableName,
            Key={
                'DeviceId': {
                    'S': received_DeviceId,
                },
                'DateTime':{
                    'S': received_DateTime,
                }
            },
        ConsistentRead=True,
        ReturnConsumedCapacity='TOTAL',
        )
        json_data = json.dumps(response)
        print("\nReceived event from DynamoDB Table:\n{}" .format(json_data))
        json_dictionary = json.loads(json_data)
        if(len(json_dictionary) > 2):
            return [1, response]   #Returns True i.e Duplicate entry found in DynamoDB
        else:
            return [0, response]   #Returns False i.e. Duplicate entry not found in DynamoDB. But table exists
            #return json_dictionary
    except ClientError as r:
        if r.response['Error']['Code'] == 'ResourceNotFoundException':
            return [5, 'TableNotFoundException']
    #get_Latest_Item_From_DynamoDB_Table ends here



def confirmData(first_value, second_value):
    #first_value: Value received from External_event
    #second_value: Value received from DynamoDB_event
    print("Confirming Data between {} and {} ".format(first_value, second_value))
    if first_value == '-' and second_value == '-':
        print("First Value is - and Second Value is -. Will return second_value {}".format(second_value))
        return second_value
    elif first_value != '-' and second_value == '-':
        print("Second Value is -. Hence, returning first_value {}".format(first_value))
        return first_value
    elif first_value == '-' and second_value != '-':
        print("First Value is -. Hence, returning second_value {}".format(second_value))
        return second_value
    else:
        #This is hit when External_event has value and DynamoDB_event also has value
        print("No Value is -. Hence, returning first_value {}".format(first_value))
        return first_value
    #confirmData ends here


def handling_duplicate_entries(outside_event, event_from_DynamoDB, i):
    confirmed_Data = {}
    #We will confirm which values are cogent & which are '-' ,& replace values accordingly

    #Mapping parameters received from outside_event
    outside_event_DeviceId = outside_event[i]['DeviceId']
    outside_event_DateTime = outside_event[i]['DateTime']
    outside_event_mt = outside_event[i]['Milk Temperature']
    outside_event_bt = outside_event[i]['TSS Temperature']
    outside_event_ac = outside_event[i]['AC Voltage']
    outside_event_bv = outside_event[i]['Battery Voltage']

    #Mapping parameters received from DynamoDB_event
    event_from_DynamoDB_DeviceId = event_from_DynamoDB['Item']['DeviceId']['S']
    event_from_DynamoDB_DateTime = event_from_DynamoDB['Item']['DateTime']['S']
    event_from_DynamoDB_mt = event_from_DynamoDB['Item']['Milk Temperature']['S']
    event_from_DynamoDB_bt = event_from_DynamoDB['Item']['TSS Temperature']['S']
    event_from_DynamoDB_ac = event_from_DynamoDB['Item']['AC Voltage']['S']
    event_from_DynamoDB_bv = event_from_DynamoDB['Item']['Battery Voltage']['S']

    #Confirming Data between both events
    confirmed_Data['DeviceId'] = confirmData(outside_event_DeviceId, event_from_DynamoDB_DeviceId)
    confirmed_Data['DateTime'] = confirmData(outside_event_DateTime, event_from_DynamoDB_DateTime)
    confirmed_Data['Milk Temperature'] = confirmData(outside_event_mt, event_from_DynamoDB_mt)
    confirmed_Data['TSS Temperature'] = confirmData(outside_event_bt, event_from_DynamoDB_bt)
    confirmed_Data['AC Voltage'] = confirmData(outside_event_ac, event_from_DynamoDB_ac)
    confirmed_Data['Battery Voltage'] = confirmData(outside_event_bv, event_from_DynamoDB_bv)

    #Dumping confirmed data in a json file
    confirmed_Data = json.dumps(confirmed_Data)
    print("\nConfirmed Data after handling_duplicate_entries:\n{}".format(confirmed_Data))
    return confirmed_Data
    #handling_duplicate_entries ends here



def create_method_handler(received_event, complete_event):
    response_to_sent = {}
    print("\nReceived event in create_method_handler:\n{}".format(received_event))
    print("\nComplete event in create_method_handler:\n{}".format(complete_event))
    for i in range(0,len(received_event)):
        DeviceId_received = tableName_Checker(complete_event['tableName'])
        print("DeviceId_received is:\t{}".format(DeviceId_received))
        if DeviceId_received == -1:
            #-1 is obtained when tableName does not consists a '-Table' string
            return "Incorrect tableName"
        elif DeviceId_received != received_event[i]['DeviceId'] :
            # Returned DeviceId from 'tableName_Checker()' does not match DeviceId in received_event
            response_to_sent[i] = "Incorrect DeviceId for this Item"
        else:
            print("\nLoop Number {}\n for Values:\n {}".format(i, received_event[i]))
            flag, response = get_Latest_Item_From_DynamoDB_Table(received_event[i]['DeviceId'], received_event[i]['DateTime'], complete_event['tableName'])
            print("Value of Flag after get_Latest_Item_From_DynamoDB_Table:\t{}".format(flag))
            print("response from get_Latest_Item_From_DynamoDB_Table in create_method_handler:\n{}".format(response))
            if response == 'TableNotFoundException':
                #Create New Table if Table is not found
                print("\nTable is not found.\nWill Create new Table")
                set_confirmation = create_Table_In_DynamoDB(received_event[i], complete_event['tableName'])
                time.sleep(10)
                set_confirmation = create_Item_In_DynamoDB_Table(received_event[i], complete_event['tableName'])
                response_to_sent[i] =  "Created New Entry" #set_confirmation['ResponseMetadata']
            if flag == 1:
                #Duplicate Entry found
                print("\nDuplicate entry found. Will Update entry")
                final_payload_to_update = handling_duplicate_entries(received_event, response, i)
                print("\nfinal_payload_to_update is:\n{}".format(final_payload_to_update))
                set_confirmation = update_Item_in_DynamoDB_Table(final_payload_to_update, complete_event['tableName'])
                #return set_confirmation
                response_to_sent[i] = "Updated Entry" #set_confirmation['ResponseMetadata']
                #return ("Successfully Updated Entry.{}".format(set_confirmation['ResponseMetadata']))
            elif flag == 0:
                #Duplicate Entry is not found. But Table exists
                print("Table found. But entry not found. Will create new Entry")
                set_confirmation = create_Item_In_DynamoDB_Table(received_event[i], complete_event['tableName'])
                response_to_sent[i] =  "Created New Entry" #set_confirmation['ResponseMetadata']
                #return ("New Entry Successfully Added.{}".format(set_confirmation['ResponseMetadata']))
    response_to_sent = json.dumps(response_to_sent)
    print("\nThis is the response to sent:\n{}".format(response_to_sent))
    return response_to_sent
    #create_method_handler ends here


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
    #tableName = event['tableName']
    #dateTime = event['payload']['Items'][0]['DateTime']
    #deviceId = event['payload']['Items'][0]['DeviceId']
    if(event['operation'] == 'create'):
        response = create_method_handler(event['payload']['Items'], event)
        print("\nThis is the response obtained which will be sent:\n{}".format(response))
        return response
    elif(event['operation'] == 'read'):
        response = get_Specific_Item_From_DynamoDB_Table(event)
        return response
    elif(event['operation'] == 'delete'):
        return "You are not authorized to perform the attempted operation"
    else:
        return "Unexpected operation in json"
