# How to use python with Tick History’s REST API to expand Chain RIC

## Overview

Tick History's REST API is a Representational State Transfer (REST)-compliant API that programmatically exposes Tick History functionality on the DataScope Select platform. Client applications can be written in most programming languages, such as C#, C++, Visual Basic, Java, Python, Objective-C, and Swift.

One of favorite use case for application that using legacy SOAP-based TRTH API is to use API expanding Chain RIC and get RIC list. After user get the list, they can pass the list to retreive some specific data using other TRTH functions and they can also export the list to other application. In this article we will demonstrate how to use the new REST API to expand Chain RIC and get RIC list like the legacy API.

This example demonstrate how to interact with the TRTH REST API without using the .Net SDK. And we use Python programming language to demonstrate the API usages as it works as script and it can works across OS.  This example applies knowledge from TRTH document and tutorial from developer community website especially steps from **Chapter 4: Expanding a Chain RIC over a Date Range** from [**USE CASES REFERENCE**](https://developers.thomsonreuters.com/sites/default/files/Thomson%20Reuters%20Tick%20History%2011.0%20REST%20API%20Use%20Cases%20Reference%20v1.0.pdf) document .
 
## Introduction

The Legacy SOAP API has ExpandChain method which will return a list of the RICs for all instruments that were part of the given chain at any time during the given time period. This Function expands the chain for the given RIC independently on each day in the requested range of dates and then collates the results as a single list of RICs. For the new REST API, client can expand chain RIC and get underlying RIC using HTTP endpoint **/Search/HistoricalChainResolution**. The API calls resolve current and past chain constituents given a Chain RIC. Instruments may be currently active, or inactive. It can be very time consuming on both SOAP and REST API. Try not use this Function with large ranges of dates.
 
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

From the HTTP response, it presents the chain’s constituent RICs. Hence the application has to parse JSON object and get RIC list by access the value of Constituents.

### Python Example 
 
#### Prerequisite

* To run the example user should have python 2.7 or 3.6 installed on OS. User can download python installer from below link. Basically user can open the example with any text editor. There are a free Python IDE such as PyCharm Community edition and Visual Studio Code user can use to open python source file.
```text
https://www.python.org
```
* In order to access Tick Historical end point, user must have DSS account with permission to access Tick Historical’s REST API. Please contact Thomson Reuters Account representative if you need a new account or additional permission.
 
* To use HTTP request and response, This example use Python requests module. If user don’t have requests installed in python library

* This example use pandas data frame and some function from numpy to parse and display data so you need install pandas and numpy module

#### Implementation

The example starts from import required Python modules so that user has to import requests and JSON module to the example. It also requires pandas and numpy module to convert JSON data to pandas data frame.
 
```python
from json import dumps, loads, load
from requests import post,get
...
import pandas as pd
import numpy as np
```

**Authentication**

To get Authentication Token, the example will ask user to input username and password and then send a new Authentication request to DSS server to get a new Token. After it get a new Token, it will pass the token to the the http request header. Below is the codes for request a new token from DSS server.
If user don’t want to get a new token as the old one still valid for 24 hour, feel free to modify RequestNewToken function to return valid token instead. 
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

Before sending HTTP request with a post message to HistoricalChainResolution endpoint, it required Authorization Token from previous steps with JSON payload containing Chain RIC, start date and end date. Please find sample JSON payload from section **Sample Request Body**.

In order to get underlying RICs from HTTP response message(see section **Sample Response message**), application has to acces Constituents list from JSON object and then convert the list to pandas data frame. And then it can access RIC list under the Constiuents list. Below is python codes from the example. It will print data frame contains RIC name and Status to console.

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
        json_object=loads(resp.text,object_pairs_hook=OrderedDict)
        dataFrame = pd.DataFrame.from_dict(json_object['value'][0]['Constituents'])
    else:
        print("Unable to expand chain response return status code:",resp.status_code)

    return dataFrame

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
            df=ExpandChain(_token,_jsonquery)
            ricCount=len(df['Identifier'])
            print("Found "+str(ricCount)+" RIC")
            #Filter and print online RIC name and Status
            pd.set_option('display.max_rows', ricCount)
            newDF = df.filter(items=['Identifier','Status'])
            newDF.index = np.arange(1,len(newDF)+1)
            print(newDF)
            pd.reset_option('display.max_rows')
```
**Running example**

To test the example, please run the following python command
> \>python ExpandChainREST.py

The example will ask user to input DSS username and password then it will request a new Token and pass it to HTTP request as described.  Feel free to change the following variables if you want to set chain RIC, start date, end date.

>_chainRIC="0#.FTSE"

>_startDate="2017-03-14T00:00:00.000Z"

>_endDate="2017-03-15T00:00:00.000Z"


After running the example, it will displays the following console output

```
Login to DSS Server
Send Login request
Authorization Token:_tHSMJfR5k2n4a56GCmGhhyCCYjt1AA6F5FC3DswB9ad55M5TQhpkOuK6jw5NWy3ir9Vzq5phjQ71rHkZhYrB7tA0c6eBEAVDlOK26H98YWYe9QqVSYp-5IeaMsI9QYIvB-ZxQr5xEv1Mc6u1KF9Afzbq3LtSC11qALNdIIS4JbGjNLqKJ8HgTD6VYuUa6Vc-OlXvEkIlClkUH7_tLCKNwqNZZYK7LPFxnhXWq9NhsoxAoxMOj2kRM1NnhUoCIIgOYfkyw69GEMTauLoHLyOHprN_4KsDlBQN59BQ8OAQu5c

Start Expanding Chain 0#.FTSE

Found 103 RIC
    Identifier Status
1     .AD.FTSE  Valid
2        .FTSE  Valid
3        AAL.L  Valid
4        ABF.L  Valid
5       ADML.L  Valid
6        AHT.L  Valid
7       ANTO.L  Valid
8         AV.L  Valid
9        AZN.L  Valid
10       BAB.L  Valid
11      BAES.L  Valid
12      BARC.L  Valid
13      BATS.L  Valid
14      BDEV.L  Valid
15      BLND.L  Valid
16       BLT.L  Valid
17      BNZL.L  Valid
18        BP.L  Valid
19      BRBY.L  Valid
20        BT.L  Valid
21       CCH.L  Valid
22       CCL.L  Valid
23       CNA.L  Valid
24       CPG.L  Valid
25      CRDA.L  Valid
26       CRH.L  Valid
27      CTEC.L  Valid
28       DCC.L  Valid
29       DGE.L  Valid
30      DLGD.L  Valid
31      EXPN.L  Valid
32       EZJ.L  Valid
33      FRES.L  Valid
34       GKN.L  Valid
35      GLEN.L  Valid
36       GSK.L  Valid
37       HIK.L  Valid
38      HMSO.L  Valid
39      HRGV.L  Valid
40      HSBA.L  Valid
41      ICAG.L  Valid
42       IHG.L  Valid
43       III.L  Valid
44       IMB.L  Valid
45       INF.L  Valid
46     INTUP.L  Valid
47      ITRK.L  Valid
48       ITV.L  Valid
49      JMAT.L  Valid
50       KGF.L  Valid
51      LAND.L  Valid
52      LGEN.L  Valid
53      LLOY.L  Valid
54       LSE.L  Valid
55      MCRO.L  Valid
56      MDCM.L  Valid
57      MERL.L  Valid
58       MKS.L  Valid
59      MNDI.L  Valid
60       MRW.L  Valid
61        NG.L  Valid
62       NXT.L  Valid
63       OML.L  Valid
64       PFG.L  Valid
65       PPB.L  Valid
66       PRU.L  Valid
67       PSN.L  Valid
68      PSON.L  Valid
69        RB.L  Valid
70       RBS.L  Valid
71      RDSa.L  Valid
72      RDSb.L  Valid
73       REL.L  Valid
74       RIO.L  Valid
75       RMG.L  Valid
76        RR.L  Valid
77       RRS.L  Valid
78       RSA.L  Valid
79       RTO.L  Valid
80      SBRY.L  Valid
81       SDR.L  Valid
82       SGE.L  Valid
83       SHP.L  Valid
84       SJP.L  Valid
85       SKG.L  Valid
86      SKYB.L  Valid
87        SL.L  Valid
88      SMIN.L  Valid
89       SMT.L  Valid
90        SN.L  Valid
91       SSE.L  Valid
92      STAN.L  Valid
93       SVT.L  Valid
94      TSCO.L  Valid
95      TUIT.L  Valid
96        TW.L  Valid
97      ULVR.L  Valid
98        UU.L  Valid
99       VOD.L  Valid
100      WOS.L  Valid
101      WPG.L  Valid
102      WPP.L  Valid
103      WTB.L  Valid

```

**Note**

The time to expand chain is proportional to the number of days in the date range. Do not specify longer date ranges than necessary.

#### Source Code

The sources codes can be downloaded from [ExpandChain](https://github.com/TR-API-Samples/Article.TRTH.Python.REST.ExpandChain)