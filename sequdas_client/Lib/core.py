#!/usr/bin/env python
import ConfigParser
import os
import re
import time
from xml.etree import ElementTree
import subprocess
from Lib.status_log import *
import tempfile
import MySQLdb
from Lib.message import *
import datetime
import shutil
import sys



def sequdas_config():
    try:
        config=read_config()
        confdict = {section: dict(config.items(section)) for section in config.sections()}
        return confdict
    except Exception as e :
        print(str(e),' Could not read configuration file')



def read_config():
    config = ConfigParser.RawConfigParser()
    pathname = os.path.dirname(os.path.abspath(sys.argv[0]))
    configFilePath = pathname+"/"+"Config/config.ini"
    try:
        config.read(configFilePath)
        return config
    except Exception as e :
        print(str(e))

def validate_email_address(email): 
    from validate_email import validate_email
    is_valid = validate_email(email)
    #match=re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[ca|com|org|edu]{3}$)",email)
    if is_valid:
        return 'Valid'
    else:
        return 'Invalid'

def get_excluded_list(logfile):
    exclude_Dir=[]
    uncompleted_Dir=[]
    if not os.path.exists(logfile):
        logfilelist = open(logfile, "a")
        logfilelist.close
    logfilelist = open(logfile, "r")
    for line in logfilelist:
        if len(line.strip()) == 0:
            continue
        if (int(line.split("\t")[5])>0 or int(line.split("\t")[5])==-1):
            exclude_Dir.append(line.split("\t")[2])
        if (int(line.split("\t")[5])==-2):
            uncompleted_Dir.append(line.split("\t")[2])
#        matchStatus1 = re.match("Status_OK", line.split("\t")[5])
#        matchStatus2 = re.match("Status_Deleted", line.split("\t")[5])
#        matchStatus3 = re.match("Uploading", line.split("\t")[5])
#        matchStatus4 = re.match("Errors", line.split("\t")[5])
#        if matchStatus1 or matchStatus2 or matchStatus3 or matchStatus4:
#            exclude_Dir.append(line.split("\t")[2])
    logfilelist.close
    return exclude_Dir,uncompleted_Dir

def SubDirPath(dirname):
    folder=[]
    listOfFiles = os.listdir(dirname)
    for item in listOfFiles:
        check_dir=os.path.join(dirname, item)
        if os.path.isdir(check_dir):
            folder.append(check_dir)
    return folder

def check_create_folder(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            print "make directory error, please check "+dirname

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def get_backup_list(directory, exclude_dirs):
    folder_paths = []
    folder_error_run=[]
    other_run=[]
    check_list = ["CompletedJobInfo.xml", "RTAComplete.txt", "SampleSheet.csv"]
    subdirectories = SubDirPath(directory)    
    sub_dir_list = [item for item in subdirectories if item not in exclude_dirs]
    for subdir in sub_dir_list:
        num=0
        for check_single_file in check_list:
            checkpoint=subdir+"/"+check_single_file            
            if(os.path.isfile(checkpoint)):
                	num=num+1
        if num==3:
            check_single_file =subdir+"/CompletedJobInfo.xml"
            with open(check_single_file, 'rt') as f:
                tree = ElementTree.parse(f)
                root = tree.getroot()
                for child in root:
                    if re.search("Error",child.tag, re.IGNORECASE):
                        if re.search("Error",child.text,re.IGNORECASE):
                            num=0
                            folder_error_run.append(subdir)
                            #print "There was some errors occured in the run "+subdir+". It has been excluded from backup"
        else:
            other_run.append(subdir)
        if (num==3):
            folder_paths.append(subdir)           
    return folder_paths,folder_error_run,other_run
    
def getID(fname):
    s_config=sequdas_config()
    ID_prefix=s_config['basic']['id_prefix']
    with open(fname, 'rb') as fp:
        lines = fp.readlines()
        if len(lines)>0:
            for line in open(fname):
                pass
            item=line.split()
            return item[0]
        else:
            item=ID_prefix+"000000"
            return item

def getlastID():
    s_config=sequdas_config()
    ID_prefix=s_config['basic']['run_id_prefix']
    mysql_host=s_config['mysql_account']['mysql_host']
    mysql_user=s_config['mysql_account']['mysql_user']
    mysql_passwd=s_config['mysql_account']['mysql_passwd']
    mysql_db=s_config['mysql_account']['mysql_db']
    myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
    cur = myConnection.cursor()
    cur.execute("SELECT bccdc_id FROM `status_table` order by id desc LIMIT 1")
    data = cur.fetchone()
    cur.close()
    #print data[0]
    if(data):
        return data[0]
    else:
        newid=0
        newid='{:06}'.format(newid)
        newid=str(newid)
        newid1=ID_prefix+newid
        return newid1
        
def getNextID(ID):
    s_config=sequdas_config()
    ID_prefix=s_config['basic']['run_id_prefix']
    newid=int(re.search(r'\d+', ID).group())
    newid=int(newid)+1
    newid='{:06}'.format(newid)
    newid=str(newid)
    newid1=ID_prefix+newid
    return newid1


def doUpdate(bccdc_id_value,status_value):
    s_config=sequdas_config()
    mysql_host=s_config['mysql_account']['mysql_host']
    mysql_user=s_config['mysql_account']['mysql_user']
    mysql_passwd=s_config['mysql_account']['mysql_passwd']
    mysql_db=s_config['mysql_account']['mysql_db']
    myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    cur = myConnection.cursor()
    cur.execute(("UPDATE information SET status=%s,end_time=%s WHERE bccdc_id=%s"),(status_value,timestamp,bccdc_id_value))
    myConnection.commit()
    myConnection.close()

def md5_compare(data_server,run_path,run_id,data_dir_server,logfile_dir):
    f_remote = open(logfile_dir+run_id+"remote.md5.tmp", "w")
    f_compare = open(logfile_dir+run_id+"compare_result.tmp", "w")
    location_remotemd5=logfile_dir+run_id+"remote.md5.tmp"
    final_md5=logfile_dir+run_id+"_md5"
    error_md5=logfile_dir+run_id+"_error_md5"
    location_compare_result=logfile_dir+run_id+"compare_result.tmp"
    if os.path.isdir(run_path):
        remotemd5 = subprocess.Popen(["ssh", data_server, "md5deep","-r","-s",data_dir_server],stdout=f_remote);
        remotemd5.wait()
        matchObj = re.match( r'\/\/', run_path)
        ###handle issue with net mapped drive "//" cannot be recognized by md5deep in cygwin
        if matchObj:
            folder_name= os.path.basename(os.path.normpath(run_path))
            cmd_create="ln -s "+run_path+" "+logfile_dir
            os.system(cmd_create)
            local_md5_compare=subprocess.Popen(["md5deep","-r","-X",location_remotemd5,logfile_dir+folder_name],stdout=f_compare)
            local_md5_compare.wait()
            cmd_delete="rm -fr "+logfile_dir+folder_name
            os.system(cmd_delete) 
        else:
            local_md5_compare=subprocess.Popen(["md5deep","-r","-X",location_remotemd5,run_path],stdout=f_compare);
            local_md5_compare.wait()
            
    else:
        print "please check your remote path when comparing md5"
    if os.path.exists(location_compare_result) and os.path.getsize(location_compare_result) > 0:
        file_status="md5_failed"
        return file_status
    else:
        file_status="Status_OK"
        return file_status
    f_remote.close()
    f_compare.close()
    
def judge_file_time(stringtime):
    filetime = stringtime
    filetime_format = datetime.datetime.strptime(filetime, "%Y-%m-%d#%H:%M:%S")
    nowtime = datetime.datetime.now()
    diff_days = nowtime-filetime_format
    return diff_days.total_seconds()/86400
    
def check_path_with_slash(folder):
    if not folder.endswith("/"):
        folder += "/"
    return folder
def del_end_slash(folder):
    if folder.endswith("/"):
        folder=re.sub('/$', '', folder)
    return folder
    
def get_archiving_time_db(sequdas_id):
    s_config=sequdas_config()
    ID_prefix=s_config['basic']['run_id_prefix']
    mysql_host=s_config['mysql_account']['mysql_host']
    mysql_user=s_config['mysql_account']['mysql_user']
    mysql_passwd=s_config['mysql_account']['mysql_passwd']
    mysql_db=s_config['mysql_account']['mysql_db']
    myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
    cur = myConnection.cursor()
    sql = "SELECT start_time FROM `status_table` WHERE bccdc_id = '%s'" % (sequdas_id)
    cur.execute(sql)
    data = cur.fetchone()
    cur.close()
    #print data[0]
    if(data):
        return data[0]
    else:
        return "error"
 
def del_old_file(filename):
    s_config=sequdas_config()
    logfile_dir=s_config['basic']['logfile_dir']    
    logfile_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),s_config['basic']['logfile_dir'])
    machine=s_config['basic']['sequencer']
    logfile_dir=check_path_with_slash(logfile_dir)
    logfile=logfile_dir+machine+"_sequdas_log.txt"
    data_server= s_config['server']['server_ssh_host']
    data_repository=s_config['server']['server_data_dir']
    data_repository=check_path_with_slash(data_repository)
    data_dir=data_repository+machine
    server_log_dir=data_dir    
    old_file_days_limit=int(s_config['basic']['old_file_days_limit'])
    i = open(filename, 'r')
    my_list = []
    for line in i:
        line = line.rstrip('\n')
        if len(line.strip()) == 0:
            continue
        ############################################        
        m = re.match("8", line.split("\t")[5])
        if m:
            file_archiving_time=line.split("\t")[4]
            file_archiving_time_db=get_archiving_time_db(line.split("\t")[0])
            if file_archiving_time == file_archiving_time_db and len(file_archiving_time_db) >5:
                pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}#[0-9:]{8}')
                match=pattern.match(file_archiving_time)
                if match:                
                    file_archiving_time_N=match.group()
                    if(judge_file_time(file_archiving_time_N)>old_file_days_limit):
                        my_list.append(line.split("\t")[0])
                        timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")	
                        ################################################
                        if os.path.isdir(line.split("\t")[2]):
                            shutil.rmtree(line.split("\t")[2])
                        elif os.path.isfile(line.split("\t")[2]):
                            os.remove(line.split("\t")[2])
                        else:
                            print "please check your file path"+line.split("\t")[2]
                else:
                    print "Please check the time format"
            else:
                print line.split("\t")[0]+": The time in log file is different from the time in db"
    i.close()
    logfile_dir_without_slash=del_end_slash(logfile_dir)
    if(len(my_list)>0):
        status_id=-2
        status_id_str=str(status_id)            
        for item in my_list:
            change_logfile(logfile,item,status_id_str)
            subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir])
    return my_list

def del_old_file_based_on_db():
    s_config=sequdas_config()
    ID_prefix=s_config['basic']['run_id_prefix']
    machine=s_config['basic']['sequencer']
    old_file_days_limit=int(s_config['basic']['old_file_days_limit'])
    old_file_list=[]
    old_file_list_del=[]
    run_dirs_analysis=s_config['sequencer']['run_dirs']
    run_dirs_output=s_config['sequencer']['run_dirs_output']
    mysql_host=s_config['mysql_account']['mysql_host']
    mysql_user=s_config['mysql_account']['mysql_user']
    mysql_passwd=s_config['mysql_account']['mysql_passwd']
    mysql_db=s_config['mysql_account']['mysql_db']
    mysql_table=s_config['mysql_account']['mysql_table']
    myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
    cur = myConnection.cursor()
    query="SELECT folder FROM "+mysql_table+ " WHERE start_time < DATE_SUB(SYSDATE(), INTERVAL "+str(old_file_days_limit)+" DAY) and source='"+machine+"'"+" and del_status<1"+" and status>3"
    cur.execute(query)
    data = cur.fetchall()
    for row in data:
        old_file_list.append(row[0]);
    cur.close()
    if(len(old_file_list)>0):
        for run_name in old_file_list:
            path1=check_path_with_slash(run_dirs_analysis)+run_name
            path2=check_path_with_slash(run_dirs_output)+run_name
            mark_i = 0
            if os.path.isdir(path1) or os.path.isdir(path2):
                if os.path.isdir(path1):
                    shutil.rmtree(path1,ignore_errors=True)
                    mark_i=mark_i+1
                if os.path.isdir(path2):
                    shutil.rmtree(path2,ignore_errors=True)
                    mark_i=mark_i+1
                if(mark_i>0):
                    old_file_list_del.append(run_name);
                    myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
                    cur = myConnection.cursor()
                    update_status="UPDATE "+mysql_table+" set del_status='1' WHERE folder='"+run_name+"' and source='"+machine+"'";
                    cur.execute(update_status)
                    myConnection.commit()
                    cur.close()
    return old_file_list_del

def remove_csv_file():
    files = os.listdir(os.curdir)
    for file in files:
        if file.endswith(".csv"):
            os.remove(os.path.join(os.curdir,file))

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
#################################################  

if __name__ == "__main__":
    read_config()