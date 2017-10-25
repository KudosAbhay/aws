Complete Documentation is based on this [link](http://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)

There are two Kinds of Developers who use API Gateway:

1. **App Developer**

2. **API Developer**

Each API includes a set of resources and methods. A resource is a logical entity that an app can access through a resource path.

For example, <i>/incomes</i> is the path of the resource representing the income of the app user. A resource can have one or more operations that are defined by appropriate HTTP verbs such as GET, POST, PUT, PATCH, and DELETE. A combination of a resource path and an operation identify a method of the API. For example,
1.	The POST <i>/incomes</i> method - Adds an income earned by the caller
2.	The GET <i>/expenses</i> method - Queries the reported expenses incurred by the caller.

For example, with DynamoDB as the backend, the API developer sets up the integration request to forward the incoming method request to the chosen backend. The setup includes specifications of an appropriate DynamoDB action, required IAM role and policies, and required input data transformation. The backend returns the result to API Gateway as an integration response. To route the integration response to an appropriate method response (of a given HTTP status code) to the client, you can configure the integration response to map required response parameters from integration to method. You then translate the output data format of the backend to that of the frontend, if necessary. API Gateway enables you to define a schema or model for the payload to facilitate setting up the body mapping template.


|Sr. No.| App Developer | API Developer|
|-------| ------------- | -------------|
| 1. | One who builds an application to call AWS Services through API Gateway. | One who creates and deploys an API to enable the required functionality in 	API Gateway.
| 2. | Does not need an AWS Account (provided that the API does not require IAM Permissions).      |   He must an IAM User in AWS Account that owns the API.
| 3. | -      |    Works with API Gateway Service component named <i><b>apigateway</b></i> to create, configure and deploy an API.
| 4. | -      |   Can create and manage an API by using the API Gateway management console or by API Gateway REST API.
| 5. | Works with the API Gateway service component, named <i><b>execute-api</b></i>, to invoke an API that was created or deployed in API Gateway.      |   -


**Calling the API**

There are several ways to call an API. They include:
* Using the AWS Command-Line Interface (CLI).
* Using an AWS SDK.
* You can also use a REST API client, such as <b>Postman</b>, to make raw API calls.
* You can enable API creation with AWS <b>CloudFormation</b> templates or <b>API Gateway Extensions to Swagger</b>.


**Invoking an API Method**

* API methods are invoked through frontend HTTP endpoints that you can associate with a registered custom domain name.

* Permissions to invoke a method are granted using IAM roles and policies or API Gateway custom authorizers.

* An API can present a certificate to be authenticated by the backend.

* Typically, API resources are organized in a resource tree according to the application logic. Each API resource can expose one or more API methods that must have unique HTTP verbs supported by API Gateway.

**Benefits of an API Gateway**
* API Gateway helps you deliver:
  1.  Robust
  2.  Secure
  3.  Scalable mobile and web application backends


* API Gateway allows you to securely connect mobile and web applications to business logic hosted on:
  1.  AWS Lambda
  2.  APIs hosted on Amazon EC2, or other publicly addressable web services hosted inside or outside of AWS.


* You don't need to develop and maintain infrastructure to handle authorization and access control, traffic management, monitoring and analytics, version management, and software development kit (SDK) generation.


**Using Amazon API Gateway**

To create, configure and deploy an API in API Gateway, you must have appropriate IAM policy provisioned with permissible access rights to the API Gateway control service.

To permit your API clients to invoke your API in API Gateway, you must set up the right IAM policy to allow the clients to call the API Gateway execution service.

To allow API Gateway to invoke an AWS service in the backend, API Gateway must have permissions to assume the roles required to call the backend AWS service.

When an API Gateway API is set up to use AWS IAM roles and policies to control client access, the client must sign API Gateway API requests with <i>Signature Version 4</i>.

* <b>Creating an IAM User / Group / Role in your AWS Account:</b>

  Never use your AWS root account to access API Gateway. Instead, create a new AWS Identity and Access Management (IAM) user, and then access API Gateway with that IAM User credentials.

  Create a new Admin IAM User / Group using this [link](http://docs.aws.amazon.com/apigateway/latest/developerguide/setting-up.html)

  1.  We have created a New Group named <i>'API_Gateway_Access_Admin_Group'</i> to create a group of Admin users for the API Gateway.

  2.  We have attached the following policies to this Group:
  <br/>```AmazonAPIGatewayAdministrator```
  <br/>```AmazonAPIGatewayInvokeFullAccess```

  3.  We have created a User named <i>'API_Gateway_Access_Admin_User'</i> and inserted into the above mentioned group by providing <b>Programmatic Access</b> and <b>AWS Management Console Access</b>.

  Create a new Invoking IAM User / Group using this [link](http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-iam-policy-examples-for-api-execution.html)

  i.  We have created a New Group named <i>'API_Gateway_Access_User_Group'</i> to create a group of users for the API Gateway.

  ii.  We have attached the following policies to this Group:
  <br/>
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": [
        "arn:aws:execute-api:REGION-NAME:*:API-ID/STAGE/POST/mydemoresource/*"
        ]
    }
    ]
  }
```
<br/>
    iii. We have created a User named <i>'API_Gateway_Access_User'</i> and inserted into the above mentioned group by providing <b>Programmatic Access'</b>.




* <b>Creating a Sample API from an Example given on this [link](http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-from-example.html) under your Admin User named <i>'API_Gateway_Admin_User'</i></b>





This is how we have created successfully an AWS API Endpoint which is accessible for all users without any credentials.
