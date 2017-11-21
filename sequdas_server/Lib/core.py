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
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:tk",["help", "in_dir=","out_dir="])
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
        elif opt =='-t':
            run_style = "True"
        elif opt =='-k':
            keep_kraken = "True"
        else:
            inputfile=""
    if len(inputfile)<1 or len(outfile)<1:
        usage()      
        sys.exit(2)
    return (inputfile, outfile,step,run_style,keep_kraken)
        
def usage():
    usage = """
    irida_uploader_com.py -i <input_directory>
    
    -h --help
    -i --in_dir    input_directory
    -o --out_dir    input_directory
    -s --step  step
       step 1: Run MiSeq reporter
       step 2: Run FastQC
       step 3: Run MultiQC
       step 4: Run Kraken
       step 5: Run IRIDA uploader
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
    rsyncproc = subprocess.Popen(rsynccmd,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        )
    a=rsyncproc.wait()


def run_machine_QC(directory,out_dir):
    command_list1=["plot_by_cycle","plot_by_lane","plot_flowcell","plot_qscore_histogram","plot_qscore_heatmap","plot_sample_qc"]
    command_list2=["summary","index-summary"]
    filetype_list=["_ClusterCount-by-lane.png","_flowcell-Intensity.png","_Intensity-by-cycle_Intensity.png","_q-heat-map.png","_q-histogram.png","_sample-qc.png"]
    run_folder_name=os.path.basename(os.path.normpath(directory))
    run_analysis_folder=out_dir+"/"+run_folder_name
    for command in command_list1:
        filename_output=run_analysis_folder+"/"+run_folder_name+"_"+command+".csv"
        try: 
            with open(filename_output, 'w') as output_file:
                p1 = subprocess.Popen([command,directory],stdout=output_file)
            output_file.close()
            a=p1.wait()
            if(a==0):
                try:
                    plot_command='gnuplot '+filename_output
                    run_plot = subprocess.Popen(plot_command,shell=True,stdout=subprocess.PIPE,)
                except:
                    print "Error, please check gnuplot!"                            
        except:
            print "Errors, please check "+command
    for command in command_list2:
        filename_output=run_analysis_folder+"/"+run_folder_name+"_"+command+".txt"
        try: 
            with open(filename_output, 'w') as output_file:
                p1 = subprocess.Popen([command,directory],stdout=output_file)
            output_file.close()
            a=p1.wait()                              
        except:
            print "Errors, please check "+command 

    for extention in filetype_list:
        src=run_folder_name+extention
        try:
           shutil.move(src,run_analysis_folder)
        except:
           os.remove(src)
    samplesheet_file=directory+"/"+"SampleSheet.csv"
    
    shutil.copy(samplesheet_file,run_analysis_folder)
    subprocess.call(['chmod', '755', run_analysis_folder+"/"+"SampleSheet.csv"])

def run_fastqc(directory,out_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    fastq_files = os.listdir(fastq_file_location)
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
           p1 = subprocess.Popen(['fastqc' ,fastq_file_location+fastq_file])
           a=p1.wait()
    fastqc_results = os.listdir(fastq_file_location)
    for fastqc_result in fastqc_results:
        matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(_fastqc.html)', fastqc_result, re.M|re.I)
        if matchObj:
            if(matchObj.group(2)=="R1"):
                shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_F.html")                  
            if(matchObj.group(2)=="R2"):
                shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_R.html")   

def run_multiQC(directory,out_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    multQC_result=run_folder_name+"_"+"qcreport"+".html"
    run_analysis_folder=out_dir+"/"+run_folder_name
    check_folder(run_analysis_folder)
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    p2 = subprocess.Popen(['multiqc','-n',multQC_result,'-f',fastq_file_location,'-o',run_analysis_folder]) 
    a=p2.wait()


def run_kraken(directory,out_dir,keep_kraken):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    sample_sheets=[directory+"/"+"SampleSheet.csv"]
    metadata=parse_metadata(sample_sheets[0])
    sample_list=parse_samples(sample_sheets[0])
    fastq_files = os.listdir(fastq_file_location)
    fastq_file_dict = {}
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
            matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(fastq.gz)', fastq_file, re.M|re.I)
            if matchObj:
                if(matchObj.group(2)=="R1" or matchObj.group(2)=="R2"):
                    key=matchObj.group(1)+"_"+matchObj.group(2)
                    fastq_file_dict[key]=fastq_file
    for sample in sample_list:
        sample_name_t=sample['sampleName']
        sample_name_t=sample_name_t.replace('_','-')
        print sample_name_t
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        fq_F=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R1]
        fq_R=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R2]
        try:
           p3_1 = subprocess.Popen(['kraken' ,'--preload','--threads','2','--db','/data/miseq/0.db/1.kraken_db/minikraken_20141208','--paired','--check-names','--output',run_analysis_folder+"/"+sample_name_t+"_kraken.out",'--fastq-input','--gzip-compressed',fq_F,fq_R])
           a=p3_1.wait()
           kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken.out"
           kraken_report_file=run_analysis_folder+"/"+sample_name_t+"_kraken_report.txt"
           with open(kraken_report_file, 'w') as output_file:                            
               p3_2 = subprocess.Popen(['kraken-report','--db','/data/miseq/0.db/1.kraken_db/minikraken_20141208',kraken_result_file],stdout=output_file)
               a=p3_2.wait()
           output_file.close()
           kraken_json_file=run_analysis_folder+"/"+sample_name_t+"_kraken.js"
            
           with open(kraken_json_file, 'w') as output_file:
               p3_3=subprocess.Popen(['python','kraken_parse.py','G','2','5',kraken_report_file],stdout=output_file)
               a=p3_2.wait()
           output_file.close()
           kraken_sorted_for_krona=run_analysis_folder+"/"+sample_name_t+"_krona.ini"
           with open(kraken_sorted_for_krona, 'w') as output_file:
               p3_4=subprocess.Popen(['cut','-f2,3',kraken_result_file],stdout=output_file)
               a=p3_4.wait()
           output_file.close()
           krona_result_file=run_analysis_folder+"/"+sample_name_t+"_krona.out.html"
           p3_5= subprocess.Popen(['perl','/data/miseq/1.soft/KronaTools-2.7/scripts/ImportTaxonomy.pl',kraken_sorted_for_krona,'-o', krona_result_file])
           a=p3_5.wait()
           if(keep_kraken is False):
           		p3_6= subprocess.Popen(['rm','-fr', kraken_result_file])
           		a=p3_5.wait()
        except:     
           print "error,please check Kraken"
   
   
def Upload_to_Irida(directory):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    try:
        resp_check1 = subprocess.call(['python','/data/miseq/irida_dj/irida_uploader_com.py','-i',directory],stderr=subprocess.PIPE)
        if resp_check1 == 0:
            print "data has been submitted to IRIDA"
    except:
        print "Error! please check connection"

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False