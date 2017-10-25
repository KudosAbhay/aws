# Accessing AWS Lambda function from Amazon API Gateway, which in turn will send Data to DynamoDB

**Steps**:
1.  Create and Deploy an AWS Lambda Function
2.  Create a simple DynamoDBOperations API
3.  Set the Lambda Function as a 'Destination' for the POST Method for our API
4.  Deploy the API
5.  Grant permissions that allow Amazon API Gateway to invoke the Lambda function
6.  Create DynamoDB Table with a Hash Key included
7.  Test sending an HTTPS Request


The POST Method of DynamoDBManager resource supports the following DynamoDB Operations:
1.  Create an Item
2.  Update an Item
3.  Read an Item
4.  Scan an Item
5.  Delete an Item


**Sample Request Payload to Create an Item in DynamoDB Table**
```
{
    "operation": "create",
    "tableName": "LambdaTable",
    "payload": {
        "Item": {
            "Id": "1",
            "name": "Bob"
        }
    }
}
```

The AWS API Gateway offers capabilities such as:
1.  Pass an entire HTTP Request and set the Response accordingly
2.  Map all methods of an API Resource to a single function with single mapping
3.  Map all sub-paths of a resource to a Lambda function without any additional configuration

**Procedure**:
<br />
<b>Step 1</b>:
1.  Sign up for an AWS account and create an admin user in the account
2.  Install and set up AWS CLI
    For more instructions, [check this link](http://docs.aws.amazon.com/lambda/latest/dg/setup.html)

<br />
<b>Step 2</b>:
<br />
1.  Create a Deployment Package using the sample code provided.
2.  Create an IAM Role so that the Lambda function can execute accordingly.
3.  Create the lambda function and then test it manually.

1.  To Create an AWS Lambda function deployment Package, use the following code in python:

```
from __future__ import print_function

import boto3
import json

print('Loading function')

def handler(event, context):
    '''Provide an event that contains the following keys:

      - operation: one of the operations in the operations dict below
      - tableName: required for operations that interact with DynamoDB
      - payload: a parameter to pass to the operation being performed
    '''
    #print("Received event: " + json.dumps(event, indent=2))
    operation = event['operation']

    if 'tableName' in event:
        dynamo = boto3.resource('dynamodb').Table(event['tableName'])

    operations = {
        'create': lambda x: dynamo.put_item(**x),
        'read': lambda x: dynamo.get_item(**x),
        'update': lambda x: dynamo.update_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
        'list': lambda x: dynamo.scan(**x),
        'echo': lambda x: x,
        'ping': lambda x: 'pong'
    }

    if operation in operations:
        return operations[operation](event.get('payload'))
    else:
        raise ValueError('Unrecognized operation "{}"'.format(operation))
```

<br />

Save the file as ```LambdaFunctionOverHttps.py```
Zip the file with the name ```LambdaFunctionOverHttps.zip```

<br />

2.  Create the IAM Role in AWS
<br />

Sign in to AWS console,
[using this link](https://console.aws.amazon.com/iam/)


[Follow these steps](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html)

As you follow the steps to create a role, please do the following:
  In Role Name, use ```lambda-gateway-execution-role```
  In Select Role Type, choose <b>AWS Service Roles</b>, then choose <b>AWS Lambda</b> (This grants AWS Lambda service permissions)
  After you create this IAM Role, update the Role using the following permissions policy:
<br />

```
    {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1428341300017",
      "Action": [
        "dynamodb:DeleteItem",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Sid": "",
      "Resource": "*",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow"
    }
  ]
}
```

Basically, provide your User with the following access as an admin:
```
AmazonAPIGatewayInvokeFullAccess
IAMSelfManageServiceSpecificCredentials
AWSLambdaFullAccess
AmazonDynamoDBFullAccess
AdministratorAccess
AmazonDynamoDBFullAccesswithDataPipeline
IAMReadOnlyAccess
IAMUserSSHKeys
```


Write down the ARN (Amazon Resource Name), which will be needed in the next steps

3.  Create the lambda function and then test it manually.
Upload the Deployment Package (.zip file which we have created), using AWS CLI.
```
aws lambda create-function \
--region _region_ \
--function-name LambdaFunctionOverHttps  \
--zip-file fileb://_file-path_/LambdaFunctionOverHttps.zip \
--role _execution-role-arn_  \
--handler LambdaFunctionOverHttps.handler \
--runtime _runtime-value_ \
--profile adminuser
```

Set the ```runtime-value``` as python3.6,
We have successfully create a Lambda Function using AWS CLI

To Test it manually, we will invoke the Lambda function using this code:
```
aws lambda  invoke \
--invocation-type Event \
--function-name LambdaFunctionOverHttps \
--region _region_ \
--payload file://_file-path_/input.txt \
--profile adminuser
outputfile.txt
```

Copy this JSON content in the input.txt and provide path of this file:
```
{
    "operation": "echo",
    "payload": {
        "somekey1": "somevalue1",
        "somekey2": "somevalue2"
    }
}
```

<b>Step 3</b>:
1.  Create the API using this code:
```
aws apigateway create-rest-api \
--name DynamoDBOperations \
--region _region_ \
--profile profile
```						

This shall be the response obtained:
```
{
    "name": "DynamoDBOperations",
    "id": "api-id",
    "createdDate": 1447724091
}
```

Note this API ID

Also, we will need the ID of API root resource, use this code for that:
```
aws apigateway get-resources \
--rest-api-id _api-id_
```

This shall be the response obtained:
```
{
    "items": [
        {
            "path": "/",
            "id": "root-id"
        }
    ]
}
```

2.  Create the Resource (DynamoDBManager) in the API
We will be executing the following code for the same:
```
aws apigateway create-resource \
--rest-api-id _api-id_ \
--parent-id _root-id_ \
--path-part DynamoDBManager
```

This shall be the response obtained:
```
{
    "path": "/DynamoDBManager",
    "pathPart": "DynamoDBManager",
    "id": "resource-id",
    "parentId": "root-id"
}
```

Kindly note the ID in the response. This is the ID of the resource (DynamoDBManager) that you created

3.  Create Method POST on the Resource
Use this code:
```
aws apigateway put-method \
--rest-api-id _api-id_ \
--resource-id _resource-id_ \
--http-method POST \
--authorization-type NONE
```

This shall be the response obtained:
```
{
    "apiKeyRequired": false,
    "httpMethod": "POST",
    "authorizationType": "NONE"
}
```


4.  Set the lambda function as the Destination for the POST Method:
```
$ aws apigateway put-integration \
--rest-api-id _api-id_ \
--resource-id _resource-id_ \
--http-method POST \
--type AWS \
--integration-http-method POST \
--uri arn:aws:apigateway:_aws-region_:lambda:path/2015-03-31/functions/arn:aws:lambda:_aws-region_:_aws-acct-id_:function:_your-lambda-function-name_/invocations
```

This shall be the response obtained:
```
{
    "httpMethod": "POST",
    "type": "AWS",
    "uri": "arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:aws-acct-id:function:LambdaFunctionForAPIGateway/invocations",
    "cacheNamespace": "resource-id"
}
```


Run the following command to set the POST Method response to JSON:
```
aws apigateway put-method-response \
--rest-api-id _api-id_ \
--resource-id _resource-id_ \
--http-method POST \
--status-code 200 \
--response-models "{\"application/json\": \"Empty\"}"
```

Run the following command to set the POST Method integration response to JSON:
```
aws apigateway put-integration-response \
--rest-api-id _api-id_ \
--resource-id _resource-id_ \
--http-method POST \
--status-code 200 \
--response-templates "{\"application/json\": \"\"}"
```

5.  Finally, Deploy the API
    We will deploy this API to a stage called ```prod```

```
aws apigateway create-deployment \
--rest-api-id _api-id_ \
--stage-name prod
```

This response shall be obtained:
```
{
    "id": _"deployment-id"_,
    "createdDate": 1447726017
}
```


6.  GRANT PERMISSION that allows Amazon API Gateway to invoke your Lambda function now
```
aws lambda add-permission \
--function-name _LambdaFunctionOverHttps_ \
--statement-id apigateway-test-2 \
--action lambda:InvokeFunction \
--principal apigateway.amazonaws.com \
--source-arn "arn:aws:execute-api:_region_:_aws-acct-id_:_api-id_/*/POST/DynamoDBManager"
```

Run the same command again, but this time you grant PERMISSION to your deployed API to invoke the lambda function:
```
aws lambda add-permission \
--function-name _LambdaFunctionOverHttps_ \
--statement-id apigateway-prod-2 \
--action lambda:InvokeFunction \
--principal apigateway.amazonaws.com \
--source-arn "arn:aws:execute-api:_region_:_aws-acct-id_:_api-id_/prod/POST/DynamoDBManager"
```

7.  Finally, Test sending an HTTPS Request:
    Before doing this, we will create a DynamoDB Table named ```LambdaTable (Id)``` where ```Id``` is the hash key of string type.

    We will send a Test request to insert a new record in our DynamoDB Table
```
aws apigateway test-invoke-method \
--rest-api-id _api-id_ \
--resource-id _resource-id_ \
--http-method POST \
--path-with-query-string "" \
--body "{\"operation\":\"create\",\"tableName\":\"LambdaTable\",\"payload\":{\"Item\":{\"Id\":\"1\",\"name\":\"Bob\"}}}"
```


To Access your API Via AWS Console,
<br />

Go to:
<br />

```Amazon API Gateway``` -> ```APIs``` -> ```DynamoDBOperations``` -> ```Stages``` -> ```prod```

To Access the API from various devices, please refer the below mentioned documentation:
<br />

[How to call an API](http://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-call-api.html)

<br />

[How to view Methods list](http://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-view-methods-list.html)

<br />


The above documentation is created and referenced using [this link](http://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https-example-configure-event-source.html)
