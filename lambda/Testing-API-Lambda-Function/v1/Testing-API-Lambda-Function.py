from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import time

from botocore.exceptions import ClientError
client1 = boto3.client('dynamodb')


#Creation Date: 29-September-2017
#Updation Date: 31-October-2017
# What's complete?:
# 1. Sending one common 'Added Entry' response instead of 'Update Entry' or 'Added Entry' by checking actual response whether it contains an HTTPStatusCode: 200 within
# 2. Reduction of many if-else loops with one line ternary statements
# 3. Addition of try-catch blocks in create_item(), update_item() and create_table()
# 4. Handling of 'None' Type values from incoming data
#    For this: a. handling_duplicate_entries() was added with few lines of code for None-Type Values checking
#              b. create_item() was added with few lines of code for None-Type Values checking
# What's Pending?
# 1. Handling of all missing parameters in payload is pending
#
#What's in Progress?
#1. Handling Read Method i.e. Using only one function instead of two for get_**_from_DynamoDB()
#   Changes Made Till Now: 1. Changed the get_..() function of read method
#
#

'''
CREATE Request:
{
  "operation": "create",
  "tableName": "Virginia-Table",
  "payload": {
    "Items": [
      {
        "DeviceId": "Virginia",
        "DateTime": "2017-10-30 00:01",
        "Milk Temperature": "4.5",
        "TSS Temperature": "-3.9",
        "AC Voltage": "222",
        "Battery Voltage": "0"
      },
      {
        "DeviceId": "Virginia",
        "DateTime": "2017-10-30 00:02",
        "Milk Temperature": "4.5",
        "TSS Temperature": "-3.9",
        "AC Voltage": "222",
        "Battery Voltage": "0"
      }
    ]
  }
}

Read Request:
{
  "operation": "read",
  "tableName": "Amul-Kude-Table",
  "payload": {
    "Key": {
      "DeviceId": "Amul-Kude",
      "DateTime": "2017-10-28 13:45"
    }
  }
}
'''

def create_Table_In_DynamoDB(passed_event, passed_tableName):
    print("passed_event in create_Table_In_DynamoDB:\n{}".format(passed_event))
    try:
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
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as r:
        if r.response['Error']['Code'] == 'ResourceInUseException':
            time.sleep(2)
            return "ResourceInUseException"
    #create_Table_In_DynamoDB ends here


def get_Specific_Item_From_DynamoDB_Table(passed_event):
    #This is to read Data from DynamoDB Table
    print("get_Specific_Item_From_DynamoDB_Table passed_event:\n{}\n".format(passed_event))
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
    print("Response from get_Specific_Item_From_DynamoDB_Table:\n{}\n".format(response))
    return response['Item']
    #get_Specific_Item_From_DynamoDB_Table ends here


def create_Item_In_DynamoDB_Table(passed_event, passed_tableName):
    try:
        print("\nResponse in create_Item_In_DynamoDB_Table passed_event:\n{}".format(passed_event))
        #Handling None-Type values here and replacing with '-'

        DeviceId = "-" if passed_event['DeviceId'] is None else passed_event['DeviceId']
        DateTime = "-" if passed_event['DateTime'] is None else passed_event['DateTime']
        Milk_Temperature = "-" if passed_event['Milk Temperature'] is None else passed_event['Milk Temperature']
        TSS_Temperature = "-" if passed_event['TSS Temperature'] is None else passed_event['TSS Temperature']
        AC_Voltage = "-" if passed_event['AC Voltage'] is None else passed_event['AC Voltage']
        Battery_Voltage = "-" if passed_event['Battery Voltage'] is None else passed_event['Battery Voltage']

        #This is to Create a New Entry in DynamoDB Table
        response = client1.put_item(
        TableName=passed_tableName,
        Item={
            'DeviceId': {
                'S': DeviceId, #['payload']['Items']['DeviceId'],
            },
            'DateTime': {
                'S': DateTime, #['payload']['Items']['DateTime'],
            },
            'Milk Temperature': {
                'S': Milk_Temperature, #['payload']['Items']['Milk Temperature'],
            },
            'TSS Temperature': {
                'S': TSS_Temperature, #['payload']['Items']['TSS Temperature'],
            },
            'AC Voltage': {
                'S': AC_Voltage #['payload']['Items']['AC Voltage'],
            },
            'Battery Voltage': {
                'S': Battery_Voltage #['payload']['Items']['Battery Voltage'],
            }
        },
        ReturnValues='ALL_OLD',
        ReturnConsumedCapacity='TOTAL',
        ReturnItemCollectionMetrics='SIZE',
        )
        print("create_Item_In_DynamoDB_Table created Item Successfully")
        return response['ResponseMetadata']['HTTPStatusCode']
    except ClientError as r:
        if r.response['Error']['Code'] == 'ResourceNotFoundException':
            time.sleep(2)
            # return "ResourceNotFoundException"
            return "ResourceNotFoundException"
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
    return response['ResponseMetadata']['HTTPStatusCode']
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
        response = [1, response] if (len(json_dictionary) > 2) else [0, response]
        #[1, response] if 'Duplicate entry is found in DynamoDB'
        #[0, response] if 'Table found in DynamoDB, but duplicate entry not found'
        return response
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
    Milk_Temperature = "-" if outside_event[i]['Milk Temperature'] is None else outside_event[i]['Milk Temperature']
    TSS_Temperature = "-" if outside_event[i]['TSS Temperature'] is None else outside_event[i]['Milk Temperature']
    AC_Voltage = "-" if outside_event[i]['AC Voltage'] is None else outside_event[i]['AC Voltage']
    Battery_Voltage = "-" if outside_event[i]['Battery Voltage'] is None else outside_event[i]['Battery Voltage']

    #Mapping parameters received from outside_event
    outside_event_DeviceId = outside_event[i]['DeviceId']
    outside_event_DateTime = outside_event[i]['DateTime']
    outside_event_mt = Milk_Temperature
    outside_event_bt = TSS_Temperature
    outside_event_ac = AC_Voltage
    outside_event_bv = Battery_Voltage

    #Mapping parameters received from DynamoDB_event
    event_from_DynamoDB_DeviceId = event_from_DynamoDB['Item']['DeviceId']['S']
    event_from_DynamoDB_DateTime = event_from_DynamoDB['Item']['DateTime']['S']
    event_from_DynamoDB_mt = event_from_DynamoDB['Item']['Milk Temperature']['S']
    event_from_DynamoDB_bt = event_from_DynamoDB['Item']['TSS Temperature']['S']
    event_from_DynamoDB_ac = event_from_DynamoDB['Item']['AC Voltage']['S']
    event_from_DynamoDB_bv = event_from_DynamoDB['Item']['Battery Voltage']['S']

    #We will confirm which values are cogent & which are '-' ,& replace values accordingly
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
        elif DeviceId_received != received_event[i]['DeviceId']:
            # Returned DeviceId from 'tableName_Checker()' does not match DeviceId in received_event
            response_to_sent[i] = "Incorrect DeviceId for this Item"
        else:
            print("\nLoop Number {}\n for Values:\n {}".format(i, received_event[i]))
            flag, response = get_Latest_Item_From_DynamoDB_Table(received_event[i]['DeviceId'], received_event[i]['DateTime'], complete_event['tableName'])
            print("Value of Flag after get_Latest_Item_From_DynamoDB_Table:\t{}".format(flag))
            print("response from get_Latest_Item_From_DynamoDB_Table in create_method_handler: {}".format(response))

            if response == 'TableNotFoundException':
                #Create New Table if Table is not found
                print("\nTable is not found.\nWill Create new Table")
                set_confirmation = create_Table_In_DynamoDB(received_event[i], complete_event['tableName'])
                print("Response from create_Table_In_DynamoDB:\n{}\n".format(set_confirmation))
                time.sleep(10)
                set_confirmation = create_Item_In_DynamoDB_Table(received_event[i], complete_event['tableName'])
                print("Response from create_Item_In_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Added Entry' if (str(set_confirmation).find("200") > -1) else "Error"

            if flag == 1:
                #Duplicate Entry found
                print("\nDuplicate entry found. Will Update entry")
                final_payload_to_update = handling_duplicate_entries(received_event, response, i)
                print("\nfinal_payload_to_update is:\n{}".format(final_payload_to_update))
                set_confirmation = update_Item_in_DynamoDB_Table(final_payload_to_update, complete_event['tableName'])
                print("Response from update_Item_in_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Added Entry' if (str(set_confirmation).find("200") > -1) else "Error"

            elif flag == 0:
                #Duplicate Entry is not found. But Table exists
                print("Table found. But entry not found. Will create new Entry")
                set_confirmation = create_Item_In_DynamoDB_Table(received_event[i], complete_event['tableName'])
                print("Response from create_Item_In_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Added Entry' if (str(set_confirmation).find("200") > -1) else "Error"

    response_to_sent = json.dumps(response_to_sent)
    # print("\nThis is the response which is sent by default:\n{}".format(response_to_sent))
    response_to_sent = json.loads(response_to_sent)
    print("\nThis is the response which is sent now:\n{}".format(response_to_sent))
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
        dynamo = boto3.resource('dynamodb').Table(event['tableName'])
        x = event.get['payload']
        #response = get_Specific_Item_From_DynamoDB_Table(event)
        try:
            response = dynamo.get_item(**x)
            return response
        except ClientError as c:
            if r.response['Error']['Code'] == 'ResourceNotFoundException':
                return "ResourceNotFoundException"
    else:
        return "Unexpected operation in json"
