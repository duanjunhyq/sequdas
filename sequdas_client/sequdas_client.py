#!/usr/bin/env python
######################################################################
#                                                                    #
# BCCDC MiSEQ Archiving System (Sequdas)                             #
#                                                                    #
# Version 1.5                                                        #
#                                                                    #
# 2017-11-30                                                         #
#                                                                    #
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
import paramiko
import logging

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
    check_create_folder(logfile_dir)
    logfile=logfile_dir+machine+"_sequdas_log.txt"
    logfile_details_file=logfile_dir+machine+"_sequdas_details_log.txt"
    send_email_switch=str2bool(s_config['basic']['send_email'])
    old_file_days_limit=int(s_config['basic']['old_file_days_limit'])
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
    split_pattern = re.compile(r"[;,]")
    email_list_admin=split_pattern.split(admin_emails)
    email_list=email_list_admin
    log_details=s_config['basic']['write_logfile_details']
    log_details=str2bool(log_details)
    if log_details is True:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logfile_details_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s() - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    # Compare the local time with NTP server
    if log_details is True:
        logger.info("#############################\n\n##Start running SeqUDAS \n\n")
    if check_time() is False:
        if log_details is True:
            logger.error("Check1: The time is not correct on computer, please check it\n")
        if send_email_switch is True:
            send_email(gmail_user,gmail_pass,email_list,"system time error","","")
        sys.exit()
    else:
        if log_details is True:
            logger.info("Check1: The time is correct on PC\n")
        print "Check1: The time is correct on PC"
    # Check the connection with MySQL server
    if checkMySQLdb() is False:
        if log_details is True:
            logger.error("Check2 The MySQL connection cannot be established\n")
        if send_email_switch is True:
            send_email(gmail_user,gmail_pass,email_list,"MySQL connection error","","")
        sys.exit()
    else:
        logger.info("Check2: The MySQL connection can be established\n")
    exclude_dirs,uncompleted_dir_log=get_excluded_list(logfile)
    if log_details is True:
        logger.info("Runs in log file: "+str(exclude_dirs)[1:-1]+"\n")
        logger.info("Runs have not been completed according to log file: "+str(uncompleted_dir_log)[1:-1]+"\n")
    for backup_dir in run_dir_lists:
        run_copy_list,run_with_error_list,uncompleted_dirs=get_backup_list(backup_dir,exclude_dirs)
        if log_details is True:
            logger.info("Scan folder in "+backup_dir+"\n")
            logger.info("Runs will be uploaded to server: "+str(run_copy_list)[1:-1]+"\n")
            logger.info("Runs with errors: "+str(run_with_error_list)[1:-1]+"\n")
            logger.info("Runs have not been completed"+str(uncompleted_dirs)[1:-1]+"\n")
        #Process error run       
        if(len(run_with_error_list)>0):
            if log_details is True:
                logger.info("start to process runs with error"+"\n")
            for run_with_error in run_with_error_list:            
                email_list=email_list_admin
                run_with_error_name=os.path.basename(os.path.normpath(run_with_error))
                sample_sheets=[run_with_error+"/"+"SampleSheet.csv"]
                metadata=parse_metadata(sample_sheets[0])
                investigator_list = split_pattern.split(metadata["investigatorName"])
                if log_details is True:
                    logger.info("**Run: "+run_with_error+"\n")
                for operator in investigator_list:
                    operator.replace(" ","")
                    if(validate_email_address(operator).lower()=="valid"):
                        email_list.append(operator)
                if send_email_switch is True:
                    send_email(gmail_user,gmail_pass,email_list,"Run failed",run_with_error_name,"")
                    if log_details is True:
                        logger.info("Email has been sent to "+str(email_list)[1:-1]+"\n")                
                add_status_error(logfile,machine,run_with_error_name,run_with_error)
            if log_details is True:
                logger.info("end of processing runs with error"+"\n")
        # Process uncompleted run
        run_uncompleted_to_update=[item for item in uncompleted_dir_log if item in run_copy_list]
        run_uncompleted_to_add=[item for item in uncompleted_dirs if item not in uncompleted_dir_log]
        if(len(run_uncompleted_to_update)>0):
            if log_details is True:
                logger.info("Runs have been finished since last checking: "+str(run_uncompleted_to_update)[1:-1]+"\n")
            for run_uncompleted_path in run_uncompleted_to_update:
                delete_old_uncompleted_record(logfile,run_uncompleted_path)
        if(len(run_uncompleted_to_add)>0):        	
            if log_details is True:
                logger.info("Runs that have not been finished are adding to the log file:"+str(run_uncompleted_to_add)[1:-1]+"\n")
            for run_uncompleted_path in run_uncompleted_to_add:
                folder_name=os.path.basename(os.path.normpath(run_uncompleted_path))
                add_status_uncompleted(logfile,machine,folder_name,run_uncompleted_path)
        # Process normal run
        if(len(run_copy_list)>0):
            for run_handle in run_copy_list:                
                last_ID=getlastID()
                current_ID=getNextID(last_ID)
                if log_details is True:
                    logger.info("start to process normal run:"+run_handle+"("+current_ID+")"+"\n")
                sample_sheets=[run_handle+"/"+"SampleSheet.csv"]                
                metadata=parse_metadata(sample_sheets[0])
                email_list=email_list_admin
                investigator_list = split_pattern.split(metadata["investigatorName"])
                for operator in investigator_list:
                    operator.replace(" ","")
                    if(validate_email_address(operator).lower()=="valid"):
                        email_list.append(operator)
                sample_list=parse_samples(sample_sheets[0])
                sample_infor=""
                mark=0
                uploader=0
                for sample in sample_list:
                    if(len(sample['sampleName'])>0):
                        sample_name=sample['sampleName']
                    else:
                        sample_name=sample['sequencerSampleId']
                    fastq_list=get_all_fastq_files(run_handle)
                    correct_samplename_with_underscore(fastq_list,sample_name)
                    if re.search( r'\_', sample_name):
                        sample_name=sample_name.replace("_", "-")
                    sample_name = sample_name.replace(' ', '-')
                    sample_name = sample_name.replace('.', '-')
                    if(len(sample['sampleProject'])>0):
                        sample_data = sample_name+"("+sample['sampleProject']+")"
                        uploader=1
                    else:
                        sample_data=sample_name
                    if mark==0:
                        sample_infor=sample_data
                        mark=mark+1
                    else:
                        sample_infor=sample_infor+","+sample_data
                if log_details is True:
                    logger.info("Sample infor:"+sample_infor+"\n")
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
                subprocess.call(["rsync","-q","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir])
                rsynccmd = 'rsync -artvh -q -p --chmod=ug=rwx '+ run_handle + ' '+data_server+':' + data_dir
                if log_details is True:
                    logger.info("Start archiving: "+rsynccmd+"\n")

                rsyncproc = subprocess.call(rsynccmd,shell=True)

#                while True:
#                    next_line = rsyncproc.stdout.readline().decode("utf-8")
#                    if not next_line:
#                        break
#                exitcode = rsyncproc.wait()
                if rsyncproc == 0:
                    #status 2: 	Data has been transferred. Waiting for md5 check
                    if log_details is True:
                        logger.info("Archiving process is successful"+"\n")
                    status_id=2
                    status_id_str=str(status_id)
                    change_logfile(logfile,current_ID,status_id_str)
                    subprocess.call(["rsync","-q","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir])
                    doUpdate(current_ID,status_id)
                    data_dir_server=data_dir+"/"+run_name
                    if log_details is True:
                        logger.info("Start to check md5 code"+"\n")
                    status_result=md5_compare(data_server,run_handle,current_ID,data_dir_server,logfile_dir)
                    if status_result=="Status_OK":
                        location_remotemd5=logfile_dir+current_ID+"remote.md5.tmp"
                        final_md5=logfile_dir+current_ID+".md5"
                        subprocess.call(["mv",location_remotemd5,final_md5])
                        subprocess.call(["rm",logfile_dir+current_ID+"compare_result.tmp"])
                        status_id=3
                        status_id_str=str(status_id)
                        change_logfile(logfile,current_ID,status_id_str)
                        subprocess.call(["rsync","-q","-p","--chmod=ug=rwx","-artvh",logfile_dir_without_slash,data_server+":"+server_log_dir])
                        doUpdate(current_ID,status_id)
                        if send_email_switch is True:
                            send_email(gmail_user,gmail_pass,email_list,"Data archiving finished",run_name,"")
                        if log_details is True:
                            logger.info("md5 checking is okay, waiting for analysis"+"\n")
                        ########################################
                        try:
                            ssh_key = paramiko.RSAKey.from_private_key_file(ssh_primate_key)
                            ssh = paramiko.SSHClient()
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect( hostname = "sabin.bcgsc.ca", username = "miseq", pkey = ssh_key )
                            if send_email_switch is True:
                                email_swith=" -e"
                            else:
                                email_swith=""
                            if uploader==1:
                                #stdin, stdout, stderr = ssh.exec_command("nohup  python /data/miseq/sequdas_server/sequdas_server.py -i "+run_path_on_server+" -o /data/miseq/sequdas_server/sequdas_result"+" -u "+current_ID+" -s 1 -n -t"+email_swith+" >>1.txt 2>&1 &")
                                ssh.exec_command("nohup  python /data/miseq/sequdas_server/sequdas_server.py -i "+run_path_on_server+" -o /data/miseq/sequdas_server/sequdas_result"+" -u "+current_ID+" -s 1 -n -t"+email_swith+" >>1.txt 2>&1 &")
                            else:
                                #stdin, stdout, stderr = ssh.exec_command("nohup  python /data/miseq/sequdas_server/sequdas_server.py -i "+run_path_on_server+" -o /data/miseq/sequdas_server/sequdas_result"+" -u "+current_ID+" -s 1 -t"+email_swith+" >>1.txt 2>&1 &")
                                ssh.exec_command("nohup  python /data/miseq/sequdas_server/sequdas_server.py -i "+run_path_on_server+" -o /data/miseq/sequdas_server/sequdas_result"+" -u "+current_ID+" -s 1 -n -t"+email_swith+" >>1.txt 2>&1 &")                          
                        except:
                            status_id=0
                            status_id_str=str(status_id)
                            change_logfile(logfile,current_ID,status_id_str)
                            logger.error("There is something wrong with analysis pipeline, please check connection or pipeline"+"\n")                                  
                        #########################################
                    else:
                        status_id=0
                        status_id_str=str(status_id)
                        change_logfile(logfile,current_ID,status_id_str)
                        doUpdate(current_ID,status_id)
                        if log_details is True:
                            logger.error("MD5 checking is failed, archiving process should be rerun"+"\n")
                else: 
                    status_id=0
                    status_id_str=str(status_id)
                    change_logfile(logfile,current_ID,status_id_str)
                    doUpdate(current_ID,status_id)
                    if log_details is True:
                        logger.error("Archiving process error, archiving process should be rerun"+"\n")
    old_file_list=del_old_file_based_on_db()
    if len(old_file_list)>0:
        old_file_str=', '.join(old_file_list)
        if send_email_switch is True:
            removal_title="Old data greater than "+str(old_file_days_limit)+" days have been removed";
            send_email(gmail_user,gmail_pass,email_list_admin,removal_title,old_file_str,"")
        if log_details is True:	 	
            logger.info("The run data have been deleted as it's too old: "+old_file_str+"\n")
        else:
            print "The run data have been deleted as it's too old: "+old_file_str+"\n"
    if log_details is True:	 	
        logger.info("End running SeqUDAS"+"\n")

                    
if __name__ == "__main__":
    main()


