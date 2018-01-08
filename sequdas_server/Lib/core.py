import os
from Lib.sample_sheet import *
import subprocess
import getopt
import ConfigParser
import shutil
import sys


def run_parameter(argv):
    inputfile = ''
    outfile=''
    run_style="False"
    keep_kraken="False"
    run_uploader="False"
    sequdas_id=""
    send_email_switch="False"
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:tkneu:",["help", "in_dir=","out_dir="])
    except getopt.GetoptError:   	  
        usage()      
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--in_dir"):
            inputfile = arg
        elif opt in ("-o", "--out_dir"):
            outfile = arg
        elif opt in ("-s", "--step"):
            step = arg
        elif opt in ("-u"):
            sequdas_id = arg
        elif opt =='-t':
            run_style = "True"
        elif opt =='-k':
            keep_kraken = "True"
        elif opt =='-n':
            run_uploader = "True"
        elif opt =='-e':
            send_email_switch = "True"
        else:
            inputfile=""
    if len(inputfile)<1 or len(outfile)<1:
        usage()      
        sys.exit(2)
    return (inputfile, outfile,step,run_style,keep_kraken,run_uploader,sequdas_id,send_email_switch)
        
def usage():
    usage = """
    sequdas_server.py -i <input_directory> -o <output_directory>
    
    -h --help
    -i --in_dir    input_directory (required)
    -o --out_dir    input_directory  (required)
    -s --step  step (required)
       step 1: Run MiSeq reporter
       step 2: Run FastQC
       step 3: Run MultiQC
       step 4: Run Kraken
       step 5: Run IRIDA uploader
    -u Sequdas id
    -e
       False: won't send email (default)
       True: end email.    
    -n
       False: won't run the IRIDA uploader (default)
       True: run IRIDA uploader.
    -t 
       False: only on step (default)
       True: run current step and the followings.
    -k
       False: won't keep the Kraken result (default)
       True: keep the Kraken result
    """
    print(usage)

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
    configFilePath = pathname+"/"+"Conf/config.ini"
    try:
        config.read(configFilePath)
        return config
    except Exception as e :
        print(str(e))

def check_folder(foldername):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
        return foldername

def copy_reporter(out_dir,run_folder_name):
    s_config=sequdas_config()
    ssh_host_report=s_config['reporter']['reporter_ssh_host']
    QC_img_dir=s_config['reporter']['qc_dir']
    rsynccmd = 'rsync -trvh -O '+ out_dir+"/"+run_folder_name +' '+ssh_host_report+':' + QC_img_dir
    rsyncproc = subprocess.call(rsynccmd,shell=True)
    return rsyncproc


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

def check_path_with_slash(folder):
    if not folder.endswith("/"):
        folder += "/"
    return folder
    
def del_end_slash(folder):
    if folder.endswith("/"):
        folder=re.sub('/$', '', folder)
    return folder

def check_create_folder(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            print "make directory error, please check "+dirname
