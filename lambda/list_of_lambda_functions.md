# List of Lambda Functions Available

List of all Lambda Functions currently hosted:

1.  **Lambda_from_Lambda**
  <br><i><u>Creation Date</u>:</i> 3-Oct-2017
  <br><i><u>Description</u>:</i> Able to Create a Lambda Function from a Lambda Function
  <br><i><u>Workflow</u>:</i> When Handler is Triggered, it calls callFunction() and creates a new Lambda Function by fetching code from S3 Bucket under 'Admin-Role' IAM Role.
  <br><i><u>IAM ROLE Associated</u>:</i> Admin-Role
  <br><i><u>Tiggers</u>:</i> None
  <br><i><u>Actions</u>:</i> None
  <br><i><u>Last Updated Status</u>:</i> 3-Oct-2017
  <br><i><u>Working Status</u>:</i> Working

2. **Device1-Lambda**
  <br><i><u>Creation Date</u>:</i> 26-Sep-2017
  <br><i><u>Description</u>:</i> Access provided to Maven Systems. Able to store upto 6 parameters in DynamoDB for now.
  <br><i><u>Workflow</u>:</i> When Handler is Triggered, It checks if incoming packet's operation is 'Read' / 'Create' / Other. Depending on Operation, it transfers the request to any specific function. Currently able to handle 'ResourceNotFoundException'. Also, it is able to respond back in JSON format with payload specifying if request was created, updated or rejected.
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> Device1-API
  <br><i><u>Actions</u>:</i> DynamoDB
  <br><i><u>Last Updated Status</u>:</i> 09-Oct-2017
  <br><i><u>Working Status</u>:</i> Working

3. **exp**
<br><i><u>Creation Date</u>:</i> 22-Sep-2017
<br><i><u>Description</u>:</i> Access provided to Girish and Team. Able to store upto 6 parameters in DynamoDB for now.
<br><i><u>Workflow</u>:</i> When Handler is Triggered, It checks if incoming packet's operation is 'Read' / 'Create' / Other. Depending on Operation, it transfers the request to any specific function. Currently able to handle 'ResourceNotFoundException'. Also, it is able to respond back in JSON format with payload specifying if request was created, updated or rejected.
<br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
<br><i><u>Tiggers</u>:</i> exp-API
<br><i><u>Actions</u>:</i> DynamoDB
<br><i><u>Last Updated Status</u>:</i> 13-Oct-2017
<br><i><u>Working Status</u>:</i> Working

4. **Testing-API_Lambda-Function**
  <br><i><u>Creation Date</u>:</i> 01-Oct-2017
  <br><i><u>Description</u>:</i> This is a platform for testing all further functions which are to be deployed on 'Device1-Lambda' and 'exp' Lambda functions. Currently 10 parameters are supported to read write from DynamoDB.
  <br><i><u>Workflow</u>:</i> When Handler is Triggered, It checks if incoming packet's operation is 'Read' / 'Create' / Other. Depending on Operation, it transfers the request to any specific function. Currently able to handle 'ResourceNotFoundException'. Also, it is able to respond back in JSON format with payload specifying if request was created, updated or rejected.
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> Testing-API
  <br><i><u>Actions</u>:</i> DynamoDB
  <br><i><u>Last Updated Status</u>:</i> 08-Oct-2017
  <br><i><u>Working Status</u>:</i> Working

5. **lambda-kinesis**
  <br><i><u>Creation Date</u>:</i> 02-Oct-2017
  <br><i><u>Description</u>:</i> Platform for testing Lambda to Kinesis connection
  <br><i><u>Workflow</u>:</i> When handler() is Triggered, it tries to put records in kinesis stream, then tries to describe the stream, then gets shard_iterator of the stream, then tries to get records from the stream.
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> None
  <br><i><u>Actions</u>:</i> Kinesis
  <br><i><u>Last Updated Status</u>:</i> 06-Oct-2017
  <br><i><u>Working Status</u>:</i> Describing Stream, Getting Shard Iterator, Shard Id is working. Inserting and Retrieving Data from Stream is not yet working.

6. **hello-world-python**
  <br><i><u>Creation Date</u>:</i>15-Sep-2017
  <br><i><u>Description</u>:</i> When 'MyLambdaRule' is hit, it prints values received from handler function
  <br><i><u>Workflow</u>:</i> AWS IoT hits 'MyLambdaRule' present in AWS IoT, this invokes this Lambda Function, which then displays incoming entries from AWS IoT.
  <br><i><u>IAM ROLE Associated</u>:</i> lambda_basic_execution
  <br><i><u>Tiggers</u>:</i> AWS IoT
  <br><i><u>Actions</u>:</i> None
  <br><i><u>Last Updated Status</u>:</i> 27-Sep-2017
  <br><i><u>Working Status</u>:</i> Working

7. **keyChecker_for_Incoming_Data**
  <br><i><u>Creation Date</u>:</i>
  <br><i><u>Description</u>:</i> Checks incoming json packet and sends SMS if not valid
  <br><i><u>Workflow</u>:</i> Checks incoming data in lambda_handler(), counts the total number of keys and matches it with the required number of keys. Also checks if each key is cogent or invalid. Sends an SMS accordingly
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> None
  <br><i><u>Actions</u>:</i> SNS
  <br><i><u>Last Updated Status</u>:</i> 02-Oct-2017
  <br><i><u>Working Status</u>:</i> Working

8. **LambdaFunctionOverHttps**
  <br><i><u>Creation Date</u>:</i> 06-Sep-2017
  <br><i><u>Description</u>:</i> Created Via AWS CLI. Does all opertions including read, write, delete, ping and echo on DynamoDB
  <br><i><u>Workflow</u>:</i> When incoming packet is received in handler(), it passess the event to specific operation and directly stores request in DynamoDB
  <br><i><u>IAM ROLE Associated</u>:</i> 'lambda-gateway-execution-role'
  <br><i><u>Tiggers</u>:</i> 'DynamoDBOperations' API
  <br><i><u>Actions</u>:</i> DynamoDB
  <br><i><u>Last Updated Status</u>:</i> 06-Sep-2017
  <br><i><u>Working Status</u>:</i> Working

9. **publishing_to_SNS**
  <br><i><u>Creation Date</u>:</i> 27-Sep-2017
  <br><i><u>Description</u>:</i> Simple Code to send an SMS using 'MyTopic' SNS Rule
  <br><i><u>Workflow</u>:</i> When handler() is hit, it will send a sample SMS via SNS Topic
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> None
  <br><i><u>Actions</u>:</i> SNS
  <br><i><u>Last Updated Status</u>:</i> 27-Sep-2017
  <br><i><u>Working Status</u>:</i> Working

10. **platform_for_testing**
  <br><i><u>Creation Date</u>:</i> 05-Oct-2017
  <br><i><u>Description</u>:</i> Platform for Testing any function
  <br><i><u>Workflow</u>:</i> None
  <br><i><u>IAM ROLE Associated</u>:</i> 'Admin-Role'
  <br><i><u>Tiggers</u>:</i> None
  <br><i><u>Actions</u>:</i> None
  <br><i><u>Last Updated Status</u>:</i> 18-Oct-2017
  <br><i><u>Working Status</u>:</i> Testing Phase
