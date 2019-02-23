#!/usr/bin/python
# -*- coding: UTF-8 -*-
from json import dumps, loads, load
from requests import post,get
from getpass import _raw_input as input
from getpass import getpass
from getpass import GetPassWarning
import os
from collections import OrderedDict
import pandas as pd
import numpy as np


_LoginToken=""
_chainRIC = "0#.SETI"
_startDate="2017-06-05T00:00:00.000Z"
_endDate="2017-06-17T00:00:00.000Z"

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
        message="Authentication Error Status Code: "+ str(resp.status_code) +" Message:"+dumps(loads(resp.text),indent=4)
        raise Exception(str(message))

    return loads(resp.text)['value']

def ExpandChain(token,json_payload):
    _expandChainURL = "https://hosted.datascopeapi.reuters.com/RestApi/v1/Search/HistoricalChainResolution"
    _header = {}
    _header['Prefer'] = 'respond-async'
    _header['Content-Type'] = 'application/json; odata.metadata=minimal'
    _header['Accept-Charset'] = 'UTF-8'
    _header['Authorization'] = 'Token' + token
    resp = post(_expandChainURL, data=None, json=json_payload, headers=_header)
    
    dataFrame= pd.DataFrame()
    if(resp.status_code==200):
        json_object=loads(resp.text,object_pairs_hook=OrderedDict)
        if len(json_object['value']) > 0:
            dataFrame = pd.DataFrame.from_dict(json_object['value'][0]['Constituents'])
    else:
        print("Unable to expand chain response return status code:",resp.status_code)

    return dataFrame


def main():
    try:
        print("Login to DSS Server")
        _DSSUsername=input('Enter DSS Username:')
        try:
            _DSSPassword=getpass(prompt='Enter DSS Password:')
            _token=RequestNewToken(_DSSUsername,_DSSPassword)
        except GetPassWarning as e:
             print(e)

        if(_token!=""):
            print("Authorization Token:"+_token+"\n")
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
            if df.empty:
                print("Unable to expand chain "+_chainRIC) 
                return

            ricCount=len(df['Identifier'])
            print("Found "+str(ricCount)+" RIC")
            #Filter and print only RIC name and Status columns
            pd.set_option('display.max_rows', ricCount)
            newDF = df.filter(items=['Identifier','Status'])
            newDF.index = np.arange(1,len(newDF)+1)
            print(newDF)
            pd.reset_option('display.max_rows')
              
    except Exception as ex:
        print("Exception occrus:", ex)

    return

if __name__=="__main__":
    main()
