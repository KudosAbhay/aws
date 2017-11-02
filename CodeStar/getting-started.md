# Creating a New Project in CodeStar

Refer [this](http://docs.aws.amazon.com/codestar/latest/userguide/sam-tutorial.html) link to create a new Serverless Project in CodeStar
<br>

<b>Workflow of a CodeStar project is</b>:
1.  Create a New Project in CodeStar for Serverless computing
2.  This will create the necessary resources for you
3.  Keep pushing commits on git repo / AWS CodeCommit
4.  CodeStar automatically reads new commits from repo and accordingly builds and deploys the resources needed

<br>
CodeStar automatically creates the following resources and helps you manage them through the Project Dashboard:

|Sr. No. | Resource Name     | Purpose |
| --- | ---      | ---       |
|1| <b>AWS API Gateway</b> | To read incoming data packets         |
|2| <b>AWS CloudFormation</b>     | To create and manage templates for project |
|3| <b>AWS CodeBuild</b>     | For Continuous Integration |
|4| <b>AWS CodePipeline</b>     | To Build, Test and Deploy resources |
|5| <b>AWS IAM</b>     | IAM Roles required for necessary deployment |
|6| <b>AWS Lambda</b>     | Lambda Function for Business Role Tier |
|7| <b>Amazon S3</b>     | 2 S3 Buckets - One to store associated access keys of user and other to store the complete repo as a backup |


Pricing for Individual Resources is as follows:
<br>


|Sr. No.| Resource Name     | Pricing |
| ---      | ---       | --- |
|1| <b>AWS API Gateway</b> | [check here](https://aws.amazon.com/api-gateway/pricing/)  |
|2| <b>AWS CloudFormation</b>     | [check here](https://aws.amazon.com/cloudformation/pricing/) |
|3| <b>AWS CodeBuild</b>     | [check here](https://aws.amazon.com/codebuild/pricing/) |
|4| <b>AWS CodePipeline</b>     | [check here](https://aws.amazon.com/codepipeline/pricing/) |
|5| <b>AWS IAM</b>     | [check here](https://aws.amazon.com/govcloud-us/pricing/iam/) |
|6| <b>AWS Lambda</b>     | [check here](https://aws.amazon.com/lambda/pricing/) |
|7| <b>Amazon S3</b>     | [check here](https://aws.amazon.com/s3/pricing/) |
