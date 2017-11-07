from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import time

from botocore.exceptions import ClientError
client1 = boto3.client('dynamodb')

# Version Number: v1.0.3
# Creation Date: 29-September-2017
# Updation Date: 03-November-2017
# Previous completions:
# 1. Reduction of many if-else loops with one line if-else statements
# 2. Addition of try-catch blocks in create_item(), update_item() and create_table()
# 3. Handling of 'None' Type values from incoming data
#    For this: a. handling_duplicate_entries() was added with few lines of code for None-Type Values checking
#              b. create_item() was added with few lines of code for None-Type Values checking
#
# What's complete in this version?
# 1. Handling of 'Read' Operation Successfully done
#    For this: a. tableName_Checker() call was moved from create_method_handler() to handler()
# 2. Providing appropriate Status Codes in response is done
#    For this: a. response_parser() is new function added which creates a proper response with status codes
# 3. Handling of all missing parameters in payload is done
#    For this: a. An Exception is raised if required parameters are not present in the payload
#
# What's Pending?
# 1. Increasing total number of parameters from 4 to 53 total
#    For this: a.  We need to make changes in create_Item(), update_Item() and handling_duplicate_entries() functions




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

def response_parser(passed_Status_Code, passed_response):
    response_to_sent = json.dumps(passed_response)
    response_to_sent = json.loads(response_to_sent)
    return {'statusCode': passed_Status_Code,
            'body': response_to_sent,
            'headers': {'Content-Type': 'application/json'}}

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


def get_Request_For_DynamoDB_Table(received_Operation_Type, received_TableName, received_DeviceId, received_DateTime):
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
        # print("\nReceived event from DynamoDB Table:\n{}" .format(json_data))
        if received_Operation_Type == 'create':
            json_data = json.dumps(response)
            json_dictionary = json.loads(json_data)
            response = [1, response] if (len(json_dictionary) > 2) else [0, response]
            #[1, response] if 'Duplicate entry is found in DynamoDB'
            #[0, response] if 'Table found in DynamoDB, but duplicate entry not found'
            return response
        elif received_Operation_Type == 'read':
            return response['Item']
    except ClientError as r:
        if r.response['Error']['Code'] == 'ResourceNotFoundException' and received_Operation_Type == 'create':
            return [5, "TableNotFoundException"]
        elif r.response['Error']['Code'] == 'ResourceNotFoundException' and received_Operation_Type == 'read':
            return "Not Found"
    #get_Latest_Item_From_DynamoDB_Table ends here


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


def handling_duplicate_entries(outside_event, event_from_DynamoDB):
    confirmed_Data = {}
    try:
        Milk_Temperature = "-" if outside_event['Milk Temperature'] is None else outside_event['Milk Temperature']
        TSS_Temperature = "-" if outside_event['TSS Temperature'] is None else outside_event['TSS Temperature']
        AC_Voltage = "-" if outside_event['AC Voltage'] is None else outside_event['AC Voltage']
        Battery_Voltage = "-" if outside_event['Battery Voltage'] is None else outside_event['Battery Voltage']

        #Mapping parameters received from outside_event
        outside_event_DeviceId = outside_event['DeviceId']
        outside_event_DateTime = outside_event['DateTime']
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
    except KeyError:
        #This will halt the complete further code execution
        raise Exception("Incorrect Parameters in received request")
    #handling_duplicate_entries ends here


def create_method_handler(complete_event, DeviceId_received):
    response_to_sent = {}
    print("\nComplete event in create_method_handler:\n{}".format(complete_event))
    print("\nDeviceId_received is: {}".format(DeviceId_received))
    count = len(complete_event['payload']['Items'])
    for i in range(0, count):
        if DeviceId_received != complete_event['payload']['Items'][i]['DeviceId']:
            # Returned DeviceId from 'tableName_Checker()' does not match DeviceId in received_event
            response_to_sent[i] = "Incorrect DeviceId"
        else:
            print("\nLoop Number {}\n for Values:\n {}".format(i, complete_event['payload']['Items'][i]))
            flag, response = get_Request_For_DynamoDB_Table('create', complete_event['tableName'], complete_event['payload']['Items'][i]['DeviceId'], complete_event['payload']['Items'][i]['DateTime'])
            # flag, response = get_Latest_Item_From_DynamoDB_Table(received_event[i]['DeviceId'], received_event[i]['DateTime'], complete_event['tableName'])
            print("Value of Flag after get_Latest_Item_From_DynamoDB_Table:\t{}".format(flag))
            print("response from get_Latest_Item_From_DynamoDB_Table in create_method_handler: {}".format(response))

            if response == 'TableNotFoundException':
                #Create New Table if Table is not found
                print("\nTable is not found.\nWill Create new Table")
                set_confirmation = create_Table_In_DynamoDB(complete_event['payload']['Items'][i], complete_event['tableName'])
                print("Response from create_Table_In_DynamoDB:\n{}\n".format(set_confirmation))
                time.sleep(10)
                set_confirmation = create_Item_In_DynamoDB_Table(complete_event['payload']['Items'][i], complete_event['tableName'])
                print("Response from create_Item_In_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Entry Added' if (str(set_confirmation).find("200") > -1) else "Error Adding Entry"

            if flag == 1:
                #Duplicate Entry found
                print("\nDuplicate entry found. Will Update entry")
                final_payload_to_update = handling_duplicate_entries(complete_event['payload']['Items'][i], response)
                print("\nfinal_payload_to_update is:\n{}".format(final_payload_to_update))
                set_confirmation = update_Item_in_DynamoDB_Table(final_payload_to_update, complete_event['tableName'])
                print("Response from update_Item_in_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Entry Updated' if (str(set_confirmation).find("200") > -1) else "Error Updating Entry"

            elif flag == 0:
                #Duplicate Entry is not found. But Table exists
                print("Table found. But entry not found. Will create new Entry")
                set_confirmation = create_Item_In_DynamoDB_Table(complete_event['payload']['Items'][i], complete_event['tableName'])
                print("Response from create_Item_In_DynamoDB_Table:\n{}\n".format(set_confirmation))
                response_to_sent[i] = 'Entry Added' if (str(set_confirmation).find("200") > -1) else "Error Adding Entry"

    return response_parser(201, response_to_sent)
    #create_method_handler ends here


def tableName_Checker(received_string):
    str = received_string
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
    response_to_sent = {}
    device_id = tableName_Checker(event['tableName'])
    if device_id == -1:
        #-1 is obtained when tableName does not consists a '-Table' string
        response_to_sent["Error"] = "Invalid Table Name"
        return response_parser(400, response_to_sent)
    if(event['operation'] == 'create'):
        # response = create_method_handler(event['payload']['Items'], event)
        response = create_method_handler(event, device_id)
        print("\nThis is the response obtained which will be sent:\n{}".format(response))
        return response
    elif(event['operation'] == 'read'):
        try:
            response_to_sent = get_Request_For_DynamoDB_Table('read', event['tableName'], event['payload']['Key']['DeviceId'], event['payload']['Key']['DateTime'])
            return response_parser(202, response_to_sent)
        except ClientError as c:
            if r.response['Error']['Code'] == 'ResourceNotFoundException':
                response_to_sent["Error"] = "Entry Not Found"
                return response_parser(404, response_to_sent)
        except KeyError:
            response_to_sent["Error"] = "Data not available for DateTime or Incorrect DeviceId"
            return response_parser(406, response_to_sent)
    else:
        response_to_sent["Error"] = "Invalid Operation Type"
        return response_parser(405, response_to_sent)
