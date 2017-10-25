
**POST REQUEST** for sending data on topic for AWS IoT Device:
<br>
***Topic*** for Publishing Data on AWS IoT using Python SDK: ```$aws/things/<THING NAME>/shadow/update```

***Syntax*** for Publishing Data on AWS IoT using Python SDK:
<br>
```
{
  “state”:
  {
    “desired”:
    {
      “DeviceId” : “Device2”,
      “DateTime” : “2017-10-25 11:53”,
      “Milk Temperature” : “4.5”,
      “Battery Temperature”: “-4.1”
    },
    “reported”:
    {
      “Item”:
      {
        “DeviceId” : “Device2”,
        “DateTime” : “2017-10-25 11:54”,
        “Milk Temperature” : “4.8”,
        “Battery Temperature”: “-5.3”
      }
    }
  }
}
```

**GET REQUEST** for retrieving data on topic for AWS IoT Device:
<br>

***Topic*** for Retrieving Data on AWS IoT using Python SDK: ```$aws/things/<THING NAME>/shadow```


<b>For Postman</b>:
<br>

1. Use Headers:
  * ```Content-Type: application/x-amz-json-1.0```
  * ```Host: REST API Endpoint of Thing```
  * ```X-Amz-Date: 20171025T111650Z```
2. Use Authorization Type, select <b>AWS Signature</b>, wherein you will need to insert:
  * ```AccessKey``` for IAM User which has access to AWS IoT
  * ```SecretKey``` for the same IAM User which has access to AWS IoT
  * ```AWS Region``` in which AWS IoT Thing is located
  * ```Service Name : iotdata```
