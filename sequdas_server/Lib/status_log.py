import time
import tempfile
import re

def add_status_starting(logfilename,run_name,run_path):
    i = open(logfilename, 'a+')
    timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
    i.write(run_name+"\t"+run_path+"\t"+timestamp+"\t"+"\n")
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

def update_pipe_status(filename,handle_ID,step,handle_status):
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
            t.write(line+"\t"+step+"\t"+str(handle_status)+"\t"+timestamp+"\n")
        else:
            t.write(line+"\n")
    i.close()
    t.seek(0)
    o = open(filename, "w") 
    for line in t:
        o.write(line)
    t.close()