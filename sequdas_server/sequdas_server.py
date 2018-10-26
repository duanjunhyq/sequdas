#!/usr/bin/env python
######################################################################
#																											               #
# BCCDC MiSEQ Archiving System (Sequdas)                             #
#	                                 										               #
# Version 1.5																			                   #
#																											               #
# 2017-11-30													                               #
#																											               #
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
#/data/miseq/MiSEQ_bakup_data/JUDY2/DATA_2017/DEMO3_completed_run1
#python /data/miseq/sequdas_server/sequdas_server.py -i /data/miseq/MiSEQ_bakup_data/BAM/DATA_2017/ DEMO3_completed_run2 -o test -s 1

import sys
import re
import shutil
import logging
from Lib.core import *
from Lib.status_log import *
from Lib.sample_sheet import *
from Lib.pipe import *
from Lib.status_db import *
from Lib.message import *
import json

# S1: MiSeq reporter 4
# S2: FastQC 5 
# S3: MultiQC 6 
# S4: Kraken 7
# S5: IRIDA uploader 8
                        

def main(argv):
    (input_dir, out_dir,step_id,run_style,keep_kraken,keep_kaiju,run_uploader,sequdas_id,send_email_switch)=run_parameter(argv)
    run_style=str2bool(run_style)
    keep_kraken=str2bool(keep_kraken)
    run_uploader=str2bool(run_uploader)
    send_email_switch=str2bool(send_email_switch)
    run_name=os.path.basename(os.path.normpath(input_dir))
    run_analysis_folder=out_dir+"/"+run_name
    check_folder(out_dir)
    check_folder(run_analysis_folder)
    s_config=sequdas_config()
    logfile_dir=s_config['basic']['logfile_dir']
    logfile_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),s_config['basic']['logfile_dir'])
    logfile_dir=check_path_with_slash(logfile_dir)
    check_create_folder(logfile_dir)
    logfile=logfile_dir+"sequdas_server_log.txt"
    logfile_details_file=logfile_dir+"sequdas_server_details_log.txt"
    log_details=s_config['basic']['write_logfile_details']
    log_details=str2bool(log_details)
    # Email setting
    gmail_user= s_config['email_account']['gmail_user']
    gmail_pass= s_config['email_account']['gmail_pass']
    admin_emails= s_config['basic']['admin_email']
    split_pattern = re.compile(r"[;,]")
    email_list_admin=split_pattern.split(admin_emails)
    email_list=email_list_admin
    if send_email_switch is True:
        sample_sheets=[input_dir+"/"+"SampleSheet.csv"]
        metadata=parse_metadata(sample_sheets[0])
        investigator_list = split_pattern.split(metadata["investigatorName"])
        for operator in investigator_list:
            operator.replace(" ","")
            if(validate_email_address(operator).lower()=="valid"):
                email_list.append(operator)
    if log_details is True:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logfile_details_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s() - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if log_details is True:	 	
        logger.info("##############################################\n\nStart analyzing for "+run_name+"\n")
    add_status_starting(logfile,run_name,input_dir)        
    step_id=int(step_id)
    status_on_db=""
    #################################
    if(step_id==1):
        try:
            run_machine_QC(input_dir,out_dir)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1): 	
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)
        if run_style is True:
            step_id=step_id+1
    if(step_id==2):
        try:
            run_fastqc(input_dir,out_dir)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)
        if run_style is True:
            step_id=step_id+1
    if(step_id==3):
        try:
            run_multiQC(input_dir,out_dir)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)  
        if run_style is True:
            step_id=step_id+1         
    if(step_id==4):
        try:
            run_kraken(input_dir,out_dir,keep_kraken)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)            
        if run_style is True:
            step_id=step_id+1
    if(step_id==5):
        try:
            run_kaiju(input_dir,out_dir,keep_kraken)
            copy_reporter(out_dir,run_name)
            status=1
        except:
            status=0
        update_pipe_status(logfile,run_name,str(step_id),status)
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)            
        if run_style is True:
            step_id=step_id+1
    if(step_id==6 and run_uploader is True):
        try:
            Upload_to_Irida(input_dir)
            status=1
        except:
            status=0
        if log_details is True:
            if (status==1):
               logger.info("step"+str(step_id)+" has been finished"+"\n")
            else:
               logger.info("There is something wrong with step"+str(step_id)+" . Please check!"+"\n")
        if len(sequdas_id)>0:
            status_update(sequdas_id,step_id,status)
    if send_email_switch is True:
        send_email(gmail_user,gmail_pass,email_list,"Analysis is finished",run_name,"")                
    logger.info("############################################## End"+"\n")
if __name__ == "__main__":
    main(sys.argv[1:])
