# encoding = utf-8

import os
import sys
import time
import datetime
from datetime import timedelta
import requests
import asyncio
import json

# !! NOTE: async functions do not work currently - current Splunk version is missing some modules

# validate user input for run_time - time requirement
async def validate_time_req_input(time_condition, delta_condition):
    if time_condition != '0':
        # try to time format this var; if successful - continue, if not - output error & exit.
        try:
            condition_timeformat = datetime.datetime.strptime(time_condition, '%H:%M:%S').strftime('%H:%M:%S')
        # handle error
        except Exception as e:
            sys.stderr.write(str(e))
            sys.exit(1)
        # if try is successfull continue to call check_run_time function.
        else:
            return check_run_time(condition_timeformat, delta_condition)
            
        
# check current time against time requirement condition
def check_run_time(time_condition, delta_condition):
    # check time requirement to run before executing the rest of the program
    datetime_now = datetime.datetime.now()
    time_now = datetime.datetime.strftime(datetime_now, '%Y-%m-%d %H:%M:%S')
    # define time delta of 5 minutes from time req given
    delta = datetime.timedelta(minutes=int(delta_condition))
    time_delta = (datetime.datetime.strptime(time_condition,'%H:%M:%S') + delta).strftime('%H:%M:%S')
    # get todays date - used for conversion to epoch time
    date_today = datetime.datetime.now().date()
    date_time_condition = datetime.datetime.strptime(str(date_today) + ' ' + str(time_condition), '%Y-%m-%d %H:%M:%S')
    # delta date time
    delta_datetime = datetime.datetime.strptime(str(date_today) + ' ' + str(time_delta), '%Y-%m-%d %H:%M:%S')
    
    # turn date time to epoch for comparison:
    condition_epoch = date_time_condition.strftime('%s')
    # set other time values in epoch - needed for comparison.
    time_now_epoch = datetime_now.strftime('%s')
    delta_epoch = delta_datetime.strftime('%s')
    # if current time does not match time criteria, exit program.
    if (condition_epoch <= time_now_epoch) and (time_now_epoch <= delta_epoch):
        # return True for run;
        return True
    else:
        # quit the program if does not match time criteria
        return False


#  this function generates a bearer token for later use.
async def gen_token(c_id, c_secret, org, appName, base_url, proxies, verify_ssl):
    #  accept all needed vars as arguments for the session
    
    # define the session
    s = requests.Session()
    # set credentials for Basic auth.
    s.auth = (c_id, c_secret)
    # define headers for request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "org": org,
        "ApplicationName": appName
        }
    # define request body 
    body = {
        "grant_type": "client_credentials",
        "scope": "read write serviceapi_all"
        }
    # define url for post request
    url = base_url + "/authorization/connect/token"
    # make the request
    response = s.post(url, headers=headers, data=body, proxies=proxies, verify=verify_ssl)
    # close the session after response
    s.close()
    # return the bearer token
    return response.json()["access_token"]


# async get requests to fetch all audit data 
async def get_audit_data(base_url, token, proxies, verify_ssl, helper, ew):
    # define days delta:
    try:
        timeunit_delta = int(helper.get_arg("fetch_for_past"))
        time_unit = helper.get_arg("time_unit")
        if time_unit == 'days':
            time_delta = datetime.timedelta(days=timeunit_delta)
        elif time_unit == 'hours':
            time_delta = datetime.timedelta(hours=timeunit_delta)
        elif time_unit == 'minutes':
            time_delta = datetime.timedelta(minutes=timeunit_delta)
        
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)
    # define params
    params = {
        "startTime":str(datetime.datetime.now().date() - time_delta),
        "endTime":  str(datetime.datetime.now().date())
        }
    # define headers
    headers = {
        "Authorization": f"Bearer {token}"
        }
    # put all endpoints in a list
    endpoint_list = ['/datashare/api/1.0/audit/data', '/datashare/api/1.0/audit/userevents', '/datashare/api/1.0/audit/useraccess']
    # look over all endpoints
    for endpoint in endpoint_list:
        # set url
        url = base_url + endpoint
        # make the request
        try:
            response = requests.get(url, headers=headers, params=params, proxies=proxies, verify=verify_ssl)
            # check if logs list is not empty
            if len(json.dumps(response.json()['values'])) > 0:
                # extract and jsonify the results within response.json()
                data = response.json()['values']
            else:
                break
        # handle exception error
        except Exception as e:
            sys.stderr.write(str(e))
            sys.exit(1)
        else:
            # for each log in data - write as new Splunk event
            for log in data:
                new_log = json.dumps(log)
                # output new event to splunk with ew(event_write)
                new_event = helper.new_event(str(new_log), time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
                ew.write_event(new_event)
    
# this functions is mandatory by Splunk - DO NOT delete it.
def validate_input(helper, definition):
    # This example accesses the modular input variable
    # mainfolder_path = definition.parameters.get('mainfolder_path', None)
    # subfolder_path = definition.parameters.get('subfolder_path', None)
    # username = definition.parameters.get('username', None)
    # password = definition.parameters.get('password', None)
    pass

# this function is mandatory by Splunk - DO NOT delete it.
# this is the main function that is recognised and called by Splunk configuration
def collect_events(helper, ew):
    # first get time requirement to run from user.
    time_condition = helper.get_arg("run_time")
    delta_condition = helper.get_arg("time_delta")
    # 'should_run' is used to determine if the program should execute or not
    # this bool variable is used by the check_run_time function.
    # validate time req input
    should_run = asyncio.run(validate_time_req_input(time_condition, delta_condition))
    # begin run if should_run is True
    # if should_run or (time_condition == '0'):
    if should_run or (time_condition == '0'):
        # defining all the input parameters as local variables
        client_id = helper.get_arg("client_id") 
        client_secret = helper.get_arg("client_secret")
        base_url = helper.get_arg("base_url")
        ims_org = helper.get_arg("ims_org")
        verify_ssl = helper.get_arg("verify_ssl")
        appName = helper.get_arg("app_name")
        # check for proxy; if enabled, fetch settings as dict; if not, send None.
        proxy_settings = {}
        proxies = {}
        try: 
            proxy_settings = helper.get_proxy()
            if proxy_settings['proxy_url']: 
                proxies['https'] = f"http://{proxy_settings['proxy_url']}:{proxy_settings['proxy_port']}"
            else:
                proxies = None
        except:
            proxies= None
        
        # generate a bearer token and store it in var 'token'
        token = asyncio.run(gen_token(client_id, client_secret, ims_org, appName, base_url, proxies, verify_ssl))
        # proceed to fetch data
        asyncio.run(get_audit_data(base_url, token, proxies, verify_ssl, helper, ew))