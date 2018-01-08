#!/usr/bin/env python
import os
import sys
import subprocess
import pipes
import datetime
import time
import pytz
import ntplib
from Lib.core import *
import MySQLdb
import re

def check_run_folders(folderlist):
    for backupDir in folderlist:
        if not os.path.exists(backupDir):
            print("\n\nERROR:  Plesae check run directory \n\n################################ \n\n"+backupDir+" is not available!\n\n################################")
            sys.exit()

def check_path_with_slash(folder):
    if not folder.endswith("/"):
        folder += "/"
    return folder
    
def del_end_slash(folder):
    if folder.endswith("/"):
        folder=re.sub('/$', '', folder)
    return folder

           
def check_server_folder(ssh_host,filepath_target):
    COMMAND="uname -a"
    try:
        ssh = subprocess.check_call(["ssh",ssh_host, COMMAND],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print "cannot connect to server:"+ssh_host+",please check the internet"
        sys.exit()
    try:
        resp_check = subprocess.call(['ssh', ssh_host, 'test -e ' + pipes.quote(filepath_target)],stderr=subprocess.PIPE)
        if resp_check <> 0:
            resp_create = subprocess.call(['ssh', ssh_host, 'mkdir ' + pipes.quote(filepath_target)])
    except:
            print "cannot check directory, please check the internet"

def utc_to_local(utc_dt):
    s_config=sequdas_config()
    local_time_zone=s_config['basic']['timezone']
    LOCALTIMEZONE = pytz.timezone(local_time_zone) # time zone name from Olson database
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(LOCALTIMEZONE)

def get_time_from_NTPClient():
    from time import ctime
    try:
        c = ntplib.NTPClient()
        response = c.request('europe.pool.ntp.org', version=3)
        formatted_date_with_micro_seconds =    datetime.datetime.strptime(str(datetime.datetime.utcfromtimestamp(response.tx_time)),"%Y-%m-%d %H:%M:%S.%f")
        local_dt = utc_to_local(formatted_date_with_micro_seconds)
#        #Remove micro seconds from the string
        formatted_date_with_corrections = str(local_dt).split(".")[0]
        return formatted_date_with_corrections
    except:
        print "Error At Time Sync: Let Me Check!"
        return "Error At Time Sync: Let Me Check!" 

def judge_file_time1(stringtime):
    filetime = stringtime
    filetime_format = datetime.datetime.strptime(filetime, "%Y-%m-%d %H:%M:%S")
    nowtime = datetime.datetime.now()
    diff_days = nowtime-filetime_format
    return diff_days.total_seconds()/86400



				
def check_time():
    formatted_date = get_time_from_NTPClient()
    timedif=judge_file_time1(formatted_date)
    if abs(timedif)>1:
        return False
    else:
        return True


def checkMySQLdb():
    s_config=sequdas_config()
    mysql_host= s_config['mysql_account']['mysql_host']
    mysql_user= s_config['mysql_account']['mysql_user']
    mysql_passwd= s_config['mysql_account']['mysql_passwd']
    mysql_db= s_config['mysql_account']['mysql_db']
    try:
        myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
        return True
    except:
        return False
