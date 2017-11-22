#!/usr/bin/env python
######################################################################
#																     #
# BCCDC MiSEQ Archiving System (Sequdas)                             #
#	                                 								 #
# Version 1.4													     #
#																	 #
# 2017-11-21													     #
#																	 #
# Jun Duan                                                           #
# BCCDC Public Health Laboratory                                     #
# University of British Columbia                                     #
# jun.duan@bccdc.ca                                                  #
#                                                                    #
# William Hsiao, PhD                                                 #
# Senior Scientist (Bioinformatics), BCCDC Public Health Laboratory  #
# Clinical Assistant Professor, Pathology & Laboratory Medicine, UBC #
# Adjunct Professor, Molecular Biology and Biochemistry, SFU         #
# Rm 2067a, 655 West 12th Avenue                                     #
# Vancouver, BC, V5Z 4R4                                             #
# Canada                                                             #
# Tel: 604-707-2561                                                  #
# Fax: 604-707-2603                                                  #
######################################################################


from Lib.core import *
from Lib.check import *
from Lib.status_log import *
from Lib.sample_sheet import *
from Lib.status_db import *
import spur

def main():
    s_config=sequdas_config()
    # Local setting
    run_dir_lists=s_config['sequencer']['run_dirs']
    run_dir_lists=re.sub(r"\s+", "", run_dir_lists, flags=re.UNICODE)
    run_dir_lists = tuple(run_dir_lists.split(";"))
    check_run_folders(run_dir_lists)
    machine=s_config['basic']['sequencer']
    ssh_primate_key=s_config['local']['ssh_primate_key']
    logfile_dir=s_config['basic']['logfile_dir']    
    logfile_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),s_config['basic']['logfile_dir'])
    logfile_dir=check_path_with_slash(logfile_dir)
    logfile=logfile_dir+machine+"_sequdas_log.txt"
    send_email_switch=str2bool(s_config['basic']['send_email'])
    # Remote setting
    data_server= s_config['server']['server_ssh_host']
    data_repository=s_config['server']['server_data_dir']
    data_repository=check_path_with_slash(data_repository)
    check_server_folder(data_server,data_repository)    
    data_dir=data_repository+machine
    check_server_folder(data_server,data_dir)
    server_log_dir=data_dir
    now = datetime.datetime.now()
    data_dir =data_dir+"/"+"DATA_"+str(now.year)
    check_server_folder(data_server,data_dir)
    # Email setting
    gmail_user= s_config['email_account']['gmail_user']
    gmail_pass= s_config['email_account']['gmail_pass']
    admin_emails= s_config['basic']['admin_email']
    admin_emails=re.sub(r"\s+", "", admin_emails, flags=re.UNICODE)
    email_list = admin_emails.split(";")
    # Compare the time with NTP server  
    if check_time() is False:
        print "system time error, please check the time"
        if send_email_switch is True:
            send_email(gmail_user,gmail_pass,email_list,"system time error","","")
        sys.exit()
    # Check the connection with MySQL server
    if checkMySQLdb() is False:
        print "MySQL connection error"
        if send_email_switch is True:
            send_email(gmail_user,gmail_pass,email_list,"MySQL connection error","","")
        sys.exit()
    exclude_dirs,uncompleted_dir_log=get_excluded_list(logfile)
    for backup_dir in run_dir_lists:
        run_copy_list,run_with_error_list,uncompleted_dirs=get_backup_list(backup_dir,exclude_dirs)
        #Handle run with error
        for run_with_error in run_with_error_list:
            run_with_error_name=os.path.basename(os.path.normpath(run_with_error))
            sample_sheets=[run_with_error+"/"+"SampleSheet.csv"]
            metadata=parse_metadata(sample_sheets[0])
            investigator_list = metadata["investigatorName"].split(";")
            for operator in investigator_list:
                operator.replace(" ", "")
                if(validate_email(operator).lower()=="valid"):
                    email_list.append(operator)
            if send_email_switch is True:
                send_email(gmail_user,gmail_pass,email_list,"Run failed",run_with_error_name,"")
            add_status_error(logfile,machine,run_with_error_name,run_with_error)
        # Handle with uncompleted run
        run_uncompleted=[item for item in uncompleted_dir_log if item not in uncompleted_dirs]
        for run_uncompleted_path in run_uncompleted:
            print run_uncompleted_path
            delete_old_uncompleted_record(logfile,run_uncompleted_path)
        # Handle with normal run
        for run_handle in run_copy_list:
            last_ID=getlastID()
            current_ID=getNextID(last_ID)
            sample_sheets=[run_handle+"/"+"SampleSheet.csv"]
            metadata=parse_metadata(sample_sheets[0])
            sample_list=parse_samples(sample_sheets[0])
            sample_infor=""
            mark=0
            uploader=0
            for sample in sample_list:
                sample_name=sample['sampleName']
                fastq_list=get_all_fastq_files(run_handle)
                correct_samplename_with_underscore(fastq_list,sample_name)
                if re.search( r'\_', sample_name):
                    sample_name=sample_name.replace("_", "-")
                sample_data = sample_name+"("+sample['sampleProject']+")"
                if(is_number(sample['sampleProject']) is True):
                    uploader=1
                if mark==0:
                    sample_infor=sample_data
                    mark=mark+1
                else:
                    sample_infor=sample_infor+","+sample_data
            run_name=os.path.basename(os.path.normpath(run_handle))
            run_path_on_server=data_dir+"/"+run_name
            timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
            # Start the archiving process
            # Status 1: archiving process is running
            status_id=1
            status_id_str=str(status_id)
            add_status_uploading(logfile,machine,current_ID,run_name,run_handle)
            if send_email_switch is True:
                send_email(gmail_user,gmail_pass,email_list,"Starting",run_name,"")
            doInsert(current_ID,machine,run_handle,run_name,status_id,timestamp,sample_infor)
            # Archive log file and run data            
            logfile_dir_without_slash=del_end_slash(logfile_dir)
            subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            rsynccmd = 'rsync -artvh -p --chmod=ug=rwx '+ run_handle + ' '+data_server+':' + data_dir
            rsyncproc = subprocess.Popen(rsynccmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,)
            while True:
                next_line = rsyncproc.stdout.readline().decode("utf-8")
                if not next_line:
                    break
            exitcode = rsyncproc.wait()
            if exitcode == 0:
                #status 2: 	Data has been transferred. Waiting for md5 check
                status_id=2
                status_id_str=str(status_id)
                change_logfile(logfile,current_ID,status_id_str)
                subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                doUpdate(current_ID,status_id)
                data_dir_server=data_dir+"/"+run_name
                status_result=md5_compare(data_server,run_handle,current_ID,data_dir_server,logfile_dir)
                if status_result=="Status_OK":
                    location_remotemd5=logfile_dir+"remote.md5.tmp"
                    final_md5=logfile_dir+current_ID+"_md5"
                    #print "The run "+run_name+" md5 check is good"
                    subprocess.call(["mv",location_remotemd5,final_md5],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    subprocess.call(["rm",logfile_dir+"compare_result.tmp"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    #status 3: 	Data has been transferred successfully. Waiting for QC report 1
                    status_id=3
                    status_id_str=str(status_id)
                    change_logfile(logfile,current_ID,status_id_str)
                    subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    doUpdate(current_ID,status_id)
                    if send_email_switch is True:
                        send_email(gmail_user,gmail_pass,email_list,"Data archiving finished",run_name,"")
                    ######################## Run Pipeline
                    #p1 Run MiSeq reporter
                    ####################################################################
                    # status 4: 	Data has been transferred successfully. Waiting for
                    # S1: MiSeq reporter 4
                    # S2: FastQC 5 
                    # S3: MultiQC 6 
                    # S4: Kraken 7
                    # S5: IRIDA uploader 8
                    ####################################################################
                    for step in range(1,6):
                        if step==5 and uploader==0:
                            status_id=8
                            status_id_str=str(status_id)
                            change_logfile(logfile,current_ID,status_id_str)
                            subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                            doUpdate(current_ID,status_id)
                        else:
                            try:
                                shell = spur.SshShell(hostname="sabin.bcgsc.ca", username="miseq", private_key_file=ssh_primate_key)
                                result = shell.run(["nohup","python", "/data/miseq/sequdas_server/sequdas_server.py", "-i",run_path_on_server,"-o","/data/miseq/sequdas_server/sequdas_result","-s",str(step),"&"])
                            except:
                                print "There is some error when running remote pipeline at step"+str(step)
                            try:
                                status_id=status_id+1
                                status_id_str=str(status_id)
                                change_logfile(logfile,current_ID,status_id_str)
                                subprocess.call(["rsync","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                doUpdate(current_ID,status_id)
                            except:
                                print "update information error at step"+str(step)
                    if send_email_switch is True:
                        send_email(gmail_user,gmail_pass,email_list,"Analysis is finished",run_name,"")
                else:
                    status_id=0
                    status_id_str=str(status_id)
                    change_logfile(logfile,current_ID,status_id_str)
                    doUpdate(current_ID,status_id)
            else:
                status_id=0
                status_id_str=str(status_id)
                change_logfile(logfile,current_ID,status_id_str)
                doUpdate(current_ID,status_id)
    del_old_file(logfile)

#                    
if __name__ == "__main__":
    main()


