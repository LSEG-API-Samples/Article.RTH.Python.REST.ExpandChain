#!/usr/bin/python
# -*- coding: UTF-8 -*-
from json import dumps, loads, load
from requests import post,get
from getpass import _raw_input as input
from getpass import getpass
from getpass import GetPassWarning
import os

_LoginToken=""
_chainRIC = "0#.FTSE"
_startDate="2017-06-05T00:00:00.000Z"
_endDate="2017-06-17T00:00:00.000Z"
_outputFilePath="./"
_outputFileName="RICList"

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
    _header['Prefer'] = 'respond-async, wait=5'
    _header['Content-Type'] = 'application/json; odata.metadata=minimal'
    _header['Accept-Charset'] = 'UTF-8'
    _header['Authorization'] = 'Token' + token
    resp = post(_expandChainURL, data=None, json=json_payload, headers=_header)
    item_list = []
    if(resp.status_code==200):
        #comment below line if you don't want to print response message to console 
        print(dumps(loads(resp.text),indent=4))
        json_object=loads(resp.text)
        if len(json_object['value'])>0:
            for identifier_set in json_object['value']:
                for var in identifier_set['Constituents']:
                    item_list.append(var['Identifier'])
    else:
        print("Unable to expand chain response return status code:",resp.status_code)

    return item_list


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
                
    except Exception as ex:
        print("Exception occrus:", ex)

    return

if __name__=="__main__":
    main()
