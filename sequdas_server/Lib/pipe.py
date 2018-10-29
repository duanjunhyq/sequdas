import os
import subprocess
import shutil
import re
from Lib.core import * 

def run_machine_QC(directory,out_dir):
    command_list1=["plot_by_cycle","plot_by_lane","plot_flowcell","plot_qscore_histogram","plot_qscore_heatmap","plot_sample_qc"]
    command_list2=["summary","index-summary"]
    filetype_list=["_ClusterCount-by-lane.png","_flowcell-Intensity.png","_Intensity-by-cycle_Intensity.png","_q-heat-map.png","_q-histogram.png","_sample-qc.png"]
    run_folder_name=os.path.basename(os.path.normpath(directory))
    run_analysis_folder=out_dir+"/"+run_folder_name
    samplesheet_file=directory+"/"+"SampleSheet.csv"
    print samplesheet_file
    shutil.copy(samplesheet_file,run_analysis_folder)
    subprocess.call(['chmod', '755', run_analysis_folder+"/"+"SampleSheet.csv"])
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
    

def run_fastqc(directory,out_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    fastq_files = os.listdir(fastq_file_location)
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
           p1 = subprocess.call(['fastqc' ,fastq_file_location+fastq_file])
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
    fastq_file_location=directory+"/Data/Intensities/BaseCalls"
    p2 = subprocess.call(['multiqc','-n',multQC_result,'-f',fastq_file_location,'-o',run_analysis_folder]) 


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
        #print sample['sampleName']
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
        sample_name_t=sample_name_t.replace('_','-')
        sample_name_t=sample_name_t.replace(' ','-')
        sample_name_t=sample_name_t.replace('.','-')
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        fq_F=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R1]
        fq_R=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R2]
        try:
           p3_1 = subprocess.call(['kraken' ,'--preload','--threads','2','--db','/data/miseq/0.db/1.kraken_db/minikraken_20141208','--paired','--check-names','--output',run_analysis_folder+"/"+sample_name_t+"_kraken.out",'--fastq-input','--gzip-compressed',fq_F,fq_R])
           kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken.out"
           kraken_report_file=run_analysis_folder+"/"+sample_name_t+"_kraken_report.txt"
           with open(kraken_report_file, 'w') as output_file:                            
               p3_2 = subprocess.call(['kraken-report','--db','/data/miseq/0.db/1.kraken_db/minikraken_20141208',kraken_result_file],stdout=output_file)
           output_file.close()
           kraken_json_file=run_analysis_folder+"/"+sample_name_t+"_kraken.js"
            
           with open(kraken_json_file, 'w') as output_file:
               p3_3=subprocess.call(['python','/data/miseq/kraken_parse.py','G','2','5',kraken_report_file],stdout=output_file)
           output_file.close()
           kraken_sorted_for_krona=run_analysis_folder+"/"+sample_name_t+"_krona.ini"
           with open(kraken_sorted_for_krona, 'w') as output_file:
               p3_4=subprocess.call(['cut','-f2,3',kraken_result_file],stdout=output_file)
           output_file.close()
           krona_result_file=run_analysis_folder+"/"+sample_name_t+"_krona.out.html"
           p3_5= subprocess.call(['perl','/data/miseq/1.soft/KronaTools-2.7/scripts/ImportTaxonomy.pl',kraken_sorted_for_krona,'-o', krona_result_file])
           if(keep_kraken is False):
               p3_6= subprocess.call(['rm','-fr', kraken_result_file])
               p3_7= subprocess.call(['rm','-fr', kraken_sorted_for_krona])
        except:     
           print "error,please check Kraken"
   

def run_kaiju(directory,out_dir,keep_kaiju):
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
        #print sample['sampleName']
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
        sample_name_t=sample_name_t.replace('_','-')
        sample_name_t=sample_name_t.replace(' ','-')
        sample_name_t=sample_name_t.replace('.','-')
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        fq_F=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R1]
        fq_R=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R2]
        try:
            level='genus'
            kaiju_result_file=run_analysis_folder+"/"+sample_name_t+"_kaiju.out"
            kaiju_report_sum=run_analysis_folder+"/"+sample_name_t+"_kaiju_sum.txt"
            kaiju_report_file=run_analysis_folder+"/"+sample_name_t+"_kaiju.ini"
            kaiju_html_file=run_analysis_folder+"/"+sample_name_t+"_kaiju_krona.out.html"
            kaiju_json_file=run_analysis_folder+"/"+sample_name_t+"_kaiju.js"
            p4_1 = subprocess.call(['kaiju' ,'-z','30','-t','/data/miseq/0.db/2.kaiju_db/nodes.dmp','-f','/data/miseq/0.db/2.kaiju_db/kaiju_db_nr_euk.fmi','-i',fq_F,'-j',fq_R,'-o',kaiju_result_file])
            p4_2 = subprocess.call(['kaijuReport','-t','/data/miseq/0.db/2.kaiju_db/nodes.dmp','-n','/data/miseq/0.db/2.kaiju_db/names.dmp','-i',kaiju_result_file,'-o',kaiju_report_sum,'-r',level])
            p4_3 = subprocess.call(['kaiju2krona','-t','/data/miseq/0.db/2.kaiju_db/nodes.dmp','-n','/data/miseq/0.db/2.kaiju_db/names.dmp','-i',kaiju_result_file,'-o',kaiju_report_file])
            p4_4= subprocess.call(['perl','/data/miseq/1.soft/KronaTools-2.7/scripts/ImportText.pl','-o',kaiju_html_file,kaiju_report_file])
            with open(kaiju_json_file, 'w') as output_file:
                p4_5=subprocess.call(['python','/data/miseq/sequdas_server/kaiju_parse.py',kaiju_report_sum,'5'],stdout=output_file)
            output_file.close()
            if(keep_kaiju is False):
               p4_6= subprocess.call(['rm','-fr', kaiju_result_file])
               p4_7= subprocess.call(['rm','-fr', kaiju_report_file])

        except:     
           print "error,please check Kaiju"


   
def Upload_to_Irida(directory):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    print directory
    try:
        resp_check1 =subprocess.call(['python','/data/miseq/irida_uploader_command_line/irida_uploader_com.py','-i',directory],shell=False)
        if resp_check1 == 0:
            print "data has been submitted to IRIDA"
    except:
        print "Error! please check connection"