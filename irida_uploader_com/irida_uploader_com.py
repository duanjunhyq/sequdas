######################################################################
#																											               #
# irida_uploader_com                                                 #
#	                                 										               #
# Version 1.0																			                 #
#																											               # 
# 2017-09-08													                               #
#																											               #			
# Jun Duan                                                           #
# BCCDC Public Health Laboratory                                     #
# University of British Columbia                                     #
# duanjun1981@gmail.com                                             #
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
#                                                                    #
# This script is used to submit data to IRIDA. The core code is from #
# https://github.com/phac-nml/irida-miseq-uploader by NML.           #
#                                                                    #
######################################################################

import getopt
import sys
import re
import os
from API.apiCalls import ApiCalls
from API.directoryscanner import find_runs_in_directory, DirectoryScannerTopics
from Validation.onlineValidation import project_exists, sample_exists
from Config.irida_con import *

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["help", "in_dir="])
    except getopt.GetoptError:   	  
        usage()      
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--in_dir"):
            inputfile = arg
        else:
            inputfile=""
    if inputfile:
		    print ('Input directory is:', inputfile)
		    run_uploader(inputfile)
    else:
		    usage()      
		    sys.exit(2)

        
def usage():
    usage = """
    irida_uploader_com.py -i <input_directory>
    
    -h --help
    -i --in_dir    input_directory
    """
    print(usage)

def check_fold(foldername):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
        return foldername


def run_uploader(directory):
    irida_con=irida_config()
    clientId=irida_con['basic']['clientid']
    clientSecret=irida_con['basic']['clientsecret']
    baseURL=irida_con['basic']['baseurl']
    username=irida_con['basic']['username']
    password=irida_con['basic']['password']
    api = ApiCalls(clientId, clientSecret, baseURL, username, password)
    sequencing_run=find_runs_in_directory(directory)
    rundata=sequencing_run[0]
    print rundata
    samples_to_create = filter(lambda sample: not sample_exists(api, sample), rundata.sample_list)
    run_on_server = api.create_seq_run(rundata.metadata)
    run_id = run_on_server["resource"]["identifier"]
    try:
        api.send_samples(samples_to_create)
        api.send_sequence_files(samples_list = rundata.samples_to_upload,upload_id = run_id)
        print "Data has been submitted to IRIDA, please check it online."
    except:
        print "Errors!Data has not been submitted!"
if __name__ == "__main__":
    main(sys.argv[1:])
