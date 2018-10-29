import time
import tempfile
import re

def add_status_uploading(logfilename,machine,ID,filename,filename_path):
    i = open(logfilename, 'a+')
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    i.write(ID+"\t"+machine+"\t"+filename_path+"\t"+filename+"\t"+timestamp+"\t"+"1"+"\n")
    i.close()

def add_status_error(logfilename,machine,filename,filename_path):
    i = open(logfilename, 'a+')
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    i.write("-"+"\t"+machine+"\t"+filename_path+"\t"+filename+"\t"+timestamp+"\t"+"-1"+"\n")
    i.close()

def add_status_uncompleted(logfilename,machine,filename,filename_path):
    i = open(logfilename, 'a+')
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    i.write("-"+"\t"+machine+"\t"+filename_path+"\t"+filename+"\t"+timestamp+"\t"+"-2"+"\n")
    i.close()

def delete_old_uncompleted_record(filename,filepath):
    t = tempfile.NamedTemporaryFile(mode="r+")
    i = open(filename, 'r')
    for line in i:
        line = line.rstrip('\n')
        if len(line.strip()) == 0:
            continue
        ##############################################
        m = re.match(filepath, line.split("\t")[2])
        if m:
            timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
        else:
            t.write(line+"\n")
    i.close()
    t.seek(0)
    o = open(filename, "w") 
    for line in t:
        o.write(line)
    t.close()


def change_logfile(filename,handle_ID,handle_status):
    t = tempfile.NamedTemporaryFile(mode="r+")
    i = open(filename, 'r')
    for line in i:
        line = line.rstrip('\n')
        if len(line.strip()) == 0:
            continue
        ##############################################
        m = re.match(handle_ID, line.split("\t")[0])
        if m:
            timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
            t.write(line.split("\t")[0]+"\t"+line.split("\t")[1]+"\t"+line.split("\t")[2]+"\t"+line.split("\t")[3]+"\t"+line.split("\t")[4]+"\t"+handle_status+"\t"+timestamp+"\n")
        else:
            t.write(line+"\n")
    i.close()
    t.seek(0)
    o = open(filename, "w") 
    for line in t:
        o.write(line)
    t.close()