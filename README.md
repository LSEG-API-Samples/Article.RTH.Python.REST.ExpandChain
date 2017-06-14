# How to use python with Tick History’s REST API to expand Chain RIC

## Overview

Tick History's REST API is a Representational State Transfer (REST)-compliant API that programmatically exposes Tick History functionality on the DataScope Select platform. Client applications can be written in most programming languages, such as C#, C++, Visual Basic, Java, Python, Objective-C, and Swift.

One of favorite use case for application that using legacy SOAP-based TRTH API is to use API expanding Chain RIC and get RIC list. After user get the list, they can pass the list to retreive some specific data using other TRTH functions and they can also export the list to other application. In this article we will demonstrate how to use the new REST API to expand Chain RIC and get RIC list like the legacy API.

This example demonstrate how to interact with the TRTH REST API without using the .Net SDK. And we use Python programming language to demonstrate the API usages as it works as script and it can works across OS.  This example applies knowledge from TRTH document and tutorial from developer community website especially steps from **Chapter 4: Expanding a Chain RIC over a Date Range** from [**USE CASES REFERENCE**](https://developers.thomsonreuters.com/sites/default/files/Thomson%20Reuters%20Tick%20History%2011.0%20REST%20API%20Use%20Cases%20Reference%20v1.0.pdf) document .
 
## Introduction

The Legacy SOAP API has ExpandChain method which will return a list of the RICs for all instruments that were part of the given chain at any time during the given time period. This Function expands the chain for the given RIC independently on each day in the requested range of dates and then collates the results as a single list of RICs. For the new REST API, client can expand chain RIC and get underlying RIC using HTTP endpoint **/Search/HistoricalChainResolution**. The API calls resolve current and past chain constituents given a Chain RIC. Instruments may be currently active, or inactive. It can be very time consuming on both SOAP and REST API. Try not use this Function with large ranges of dates.

Basically if Chain RIC is valid RIC, the JSON body of the Response message contains list of RIC. But in case of invalid Chain, size of RIC list will be zero or empty. Hence we assume that Chain RIC is invalid for this case.
 
### **HTTP Request**
 
* **Endpoint URL:**

```
https://hosted.datascopeapi.reuters.com/RestApi/v1/Search/HistoricalChainResolution
```


* **Method:** POST

* **Headers:**
```
Prefer: respond-async
Content-Type: application/json; odata.metadata=minimal
Authorization: <Your Authorization Token>
 ```

* **Body:**
```text
ChainRics: Identifies one or more chain RICs, each of which will be resolved into its constituent RICs.
Start: Start date. For example, 2017-01-01T00:00:00.000Z.
End: End date. For example, 2017-01-01T00:00:00.000Z.
 ```

* **Sample Request Body**
```json
 {
       "Request":
                {
                     "ChainRics": [ "0#HO:" ],
                     "Range": {
                            "Start": "2008-01-01T00:00:00.000Z",
                            "End": "2016-01-01T00:00:00.000Z"
                          }
               }
}
```

### HTTP Response
* **Sample Response message**
```
HTTP/1.1 200 OK
```

```json
 {
    "@odata.context": "https://hosted.datascopeapi.reuters.com/RestApi/v1/$metadata#Collection(ThomsonReuters.Dss.Api.Search.HistoricalChainInstrument)",
    "value": [
              {
                "Identifier": "0#HO:",
                "IdentifierType": "ChainRIC",
                "Source": "",
                "Key": "VjF8MHgxMDAwMDAwMDAwMDAwMDAwfDB4MTAwMDAwMDAwMDAwMDAwMHx8Q0hSfENIUnxDSFJ8SHx8MCNITzp8",
                "Description": "Historical Chain",
                "InstrumentType": "Unknown",
                "Status": "Valid",
                "Constituents": [
                               {             
                                  "Identifier": "HOF0",
                                  "IdentifierType": "Ric",
                                  "Source": "", "Key": "VjF8MHgzMDAwMDAwMDAwMDAwMDAwfDB4MzAwMDAwMDAwMDAwMDAwMHx8fHx8fHxIT0YwfA",
                                  "Description": "Historical Instrument",
                                  "InstrumentType": "Unknown",
                                  "Status": "Valid",
                                  "DomainCode": "6"
                               },
                                                                                                         
              . . .                                                                                           
                               {
                                 "Identifier": "HOZ9",
                                   "IdentifierType": "Ric",
                                   "Source": "",
                                   "Key": "VjF8MHgzMDAwMDAwMDAwMDAwMDAwfDB4MzAwMDAwMDAwMDAwMDAwMHx8fHx8fHxIT1o5fA",
                                   "Description": "Historical Instrument",
                                   "InstrumentType": "Unknown",
                                   "Status": "Valid",
                                   "DomainCode": "6"
                               }]
               ]
 
          }
    ]
}
```

The HTTP response presents the chain’s constituent RICs. Hence the application has to parse JSON object and get RIC list by access the value of Constituents.

### Python Example 
 
#### Prerequisite

* To run the example you should have python 2.7 or 3.6 installed on your OS. You can download python installer from below link. Basically you can open the example with any text editor. But if you want a free Python IDE we recommend PyCharm Community edition or Visual Studio Code.
```text
https://www.python.org
```
* In order to access Tick Historical end point, you must have DSS account with permission to access Tick Historical’s REST API. Please contact Thomson Reuters Account representative if you need the permission.
 
* To use HTTP request and get responses back, This example use Python requests module. If you don’t have requests installed in your library, you can install it by using pip install.

> pip install requests

#### Implementation

The example starts from import required Python modules so you have to import request and json module in the example. You need json module to parse JSON data in the HTTP response.
 
```python
from json import dumps, loads, load
from requests import post,get
```

**Authentication**

To get Authentication Token, the example will ask user to input username and password and then send a new Authentication request to DSS server to get a new Token. After it get a new Token, it will pass the token to the the http request header. Below is the codes for request a new token from DSS server.
If you don’t want to get a new token as the old one still valid for 24 hour, feel free to modify RequestNewToken function to return your token instead. 
```python
def RequestNewToken(username="",password=""):
    _AuthenURL = "https://hosted.datascopeapi.reuters.com/RestApi/v1/Authentication/RequestToken"
    _header= {}
    _header['Prefer']='respond-async'
    _header['Content-Type']='application/json; odata.metadata=minimal'
    _data={'Credentials':{
        'Password':password,
        'Username':username
        }
    }

    print("Send Login request")
    resp=post(_AuthenURL,json=_data,headers=_header)

    if resp.status_code!=200:
        message="Authentication Error Status Code: "+ str(resp.status_code) +" Message:"+resp.text
        raise Exception(dumps(message,indent=4))

    return loads(resp.text)['value']
```

**Expand Chain**

Before sending HTTP request with a post message to HistoricalChainResolution endpoint, it required Authorization Token from previous steps with JSON payload containing Chain RIC with start and end date you wan to request.You can find sample JSON payload from section **Sample Request Body**.

In order to get underlying RICs from HTTP response message(see section **Sample Response message**), application need to parse RIC name from the value of the Identifier from Constiuents JSON element. It quite easy to access the value using python, we will iterate through the value of Constituents element and then return item list at the end of ExpandChain method. After we get the item list, we can print the item list to console or write it to file. Below is python codes from the example. It will write the item list to file.

```python
def ExpandChain(token,json_payload):
    _expandChainURL = "https://hosted.datascopeapi.reuters.com/RestApi/v1/Search/HistoricalChainResolution"
    _header = {}
    _header['Prefer'] = 'respond-async, wait=5'
    _header['Content-Type'] = 'application/json; odata.metadata=minimal'
    _header['Accept-Charset'] = 'UTF-8'
    _header['Authorization'] = 'Token' + token

    resp = post(_expandChainURL, data=None, json=json_payload, headers=_header)

    item_list = []
    if(resp.status_code==200):
        json_object=loads(resp.text)
        if len(json_object['value'])>0:
            for identifier_set in json_object['value']:
                for var in identifier_set['Constituents']:
                    item_list.append(var['Identifier'])
    else:
        print("Unable to expand chain response return status code:",resp.status_code)

    return item_list
```

```python
#In the Main function
_jsonquery={
            "Request": {
                "ChainRics": [
                        _chainRIC
                        ],
                "Range": {
                    "Start": _startDate,
                    "End": _endDate
                }
             }
}

            print("Start Expanding Chain "+_chainRIC+"\n")
            item_list=ExpandChain(_token,_jsonquery)
            if(len(item_list)>0):
                 #Write Output to file.
                print("\nFound "+str(len(item_list))+" RIC under Chain RIC:"+_chainRIC)
                outputfilepath = str(_outputFilePath + _outputFileName + str(os.getpid()) + '.txt')
                fh=open(outputfilepath, 'w')
                print("Open "+outputfilepath+" for writing item list")
                for itemname in item_list:
                        linestr=itemname+"\n"
                        fh.writelines(linestr)
                print("Write output to "+outputfilepath+" completed")
                fh.close()
            else:
                print("Unable to expand chain")
```
**Running example**

To test the example, please run the following python command
> \>python ExpandChainREST.py

The example will ask user to input DSS username and password then it will request a new Token and pass it to HTTP request as described.  Feel free to change the following variables if you want to set chain RIC, start date, end date, output file path and output file name. 

>_chainRIC="0#CL+"

>_startDate="2017-03-14T00:00:00.000Z"

>_endDate="2017-03-15T00:00:00.000Z"

>_outputFilePath="./"

>_outputFileName="RICList"

After running the example, it will shows the following console output

```
C:\Articles2017\ForReview\TRTH Expand Chain>c:\Python27\python.exe ExpandChainRE
ST.py
Login to DSS Server
Enter DSS Username:9009xxx
Enter DSS Password:
Send Login request
Authorization Token:_a4tPNOXEdKiWXZ7P5j4I4-1o53yVaikzB3OaPfGTpOi2jGqxbzOanUMd0zW
fG6Ct0KIjJkqTUbslxD6tOzatrN-sJkErLxedFhHx6kJsrKigxO9MgV68q6ccQ-FEF-EuQKK3jsfGUML
oyqYPwZFKUps2oRQF9q0eA3cKyR2vOIiSmGkralV-60sxOiRq-gKqi4M9Wshkm7BmfQfPNvDsa35b-MO
bcccGjD9mJiukO0MJeui6fm88nZN__7iW7HgpgNTigt5A5H0Ct1v0XFsIf_StlLMh7n6dxlST2sDA-aI


Start Expanding Chain 0#CL+


Found 67756 RIC under Chain RIC:0#CL+
Open ./RICList10616.txt for writing item list
Write output to ./RICList10616.txt completed

```

**Note**

The time to expand chain is proportional to the number of days in the date range. Do not specify longer date ranges than necessary.

#### Source Code

You can download full Example ExpandChainREST.py source file from [Link To Source Codes](./ExpandChainREST.py)