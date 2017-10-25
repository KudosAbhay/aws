from __future__ import print_function # Python 2/3 compatibility
import boto3
client = boto3.client('lambda')

'''
Documentation:
Creating a Lambda function is referenced from:https://boto3.readthedocs.io/en/latest/reference/services/lambda.html
Contents of callFunction():
1. FunctionName : The Name of Lambda Function which is to be created
2. Runtime: Runtime Environment for Lambda Function : 'nodejs'|'nodejs4.3'|'nodejs6.10'|'java8'|'python2.7'|'python3.6'|'dotnetcore1.0'|'nodejs4.3-edge'
3. Role: ARN Role under which the function is to be created
4. Handler: Name of the Handler method of Lambda Function
5. Code: Code which is to be written in the Lambda function. This Code is stored in an S3 bucket
      {
        'S3Bucket': 'Name_of_S3_Bucket',
        'S3Key': 'Name_of_S3_Object_i.e._Zip File',
        'S3ObjectVersion': 'If_versioning_is_enabled_on_the_Object'
    }
6. Description: Description of the Lambda function
7. Timeout: Timeout Timing for the Lambda function
8. MemorySize: 'Memory Size which will be used by Lambda Function in MB'
9. Publish: Request by AWS Lambda function to create a new function and publish it. True|False
10. Tags: Tags need to be mentioned here if any for the Lambda function
'''


def callFunction():
    response = client.create_function(
        FunctionName='CreatedFromLambda',
        Runtime='python3.6',
        Role='arn:aws:iam::<ACCOUNT-ID>:role/admin-role',
        Handler='CreatedFromLambda.handler',
        Code={
            'S3Bucket': 'forlambda',
            'S3Key': 'LambdaFunctionOverHttps.zip'
            },
        Description='This is Created from Lambda Function',
        Timeout=123,
        MemorySize=512,
        Publish=True,
        Tags={
            ' ': ' '
        }
    )
    return response


def handler(event, context):
    a = callFunction()
    print(a)
