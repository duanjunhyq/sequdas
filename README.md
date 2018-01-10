# SeqUDAS: Sequence Upload and Data Archiving System

## Overview

Modern DNA sequencing machines generate several gigabytes (GB) of data per run. Organizing and archiving this data presents a challenge for small labs. We present a Sequence Upload and Data Archiving System (SeqUDAS) that aims to ease the task of maintaining a sequence data repository through process automation and an intuitive web interface.

## Features

- Automated upload and storage of sequence data to a central storage server.
- Data validation with MD5 checksums for data integrity assurance
- [Illumina modules](https://bitbucket.org/invitae/illuminate) are incorpated to parse metrics binaries and generate a report similar to Illumina SAV.
- FASTQC and MultiQC workflows are included to perform QC analysis automatically.
- A taxonomic report will be generated based on Kraken report 
- Archival information, QC results and taxonomic report can be viewed through a mobile-friendly web interface
- Pass sequence data along to another remote server via API (IRIDA) 

## Architecture

SeqUDAS consists of three components:

- Data manager: Installed on a PC directly attached to an illumina sequencing machine.
- Data analyzer: Installed on a server to run the data analysis jobs.
- Web Application: Installed on a web server to provide account management and report viewing.

<img src="https://github.com/duanjunhyq/sequdas/blob/master/docs/images/sequdas-architecture.jpg" width="600" height="150">

## Installation

The package requires:

Python 2.7

## Configuration file

You must provide a configuration file on both Data manager and Data analyzer.

Here is an example for Data Manager:

```
[basic]
sequencer = machine_name
run_id_prefix = BCCDCN
# Complete list of timizones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
timezone = Canada/Pacific
write_logfile_details = False
old_file_days_limit = 180
admin_email = test@test.com
logfile_dir = Log
send_email = False

[sequencer]
run_dirs =  //machine/MiSeqAnalysis

[local]
ssh_primate_key= /home/sequdas/.ssh/id_rsa

[server]
server_ssh_host = miseq@127.0.0.1
server_data_dir = /data/sequdas

[mysql_account]
mysql_host = 127.0.1
mysql_user = test
mysql_passwd = test
mysql_db = sequdas

[email_account]
gmail_user = test
gmail_pass = test

```

Here is an example for Data Analyzer:

```
[basic]
write_logfile_details = False
admin_email = test@test.com
logfile_dir = Log
send_email = False

[reporter]
reporter_ssh_host = test@127.0.1
qc_dir = /home/sequdas/img

[mysql_account]
mysql_host = 127.0.0.1
mysql_user = test
mysql_passwd = test
mysql_db = sequdas

[email_account]
gmail_user = test
gmail_pass = test

```

## Usage

### Data manager

SeqUDAS uses Cron to triger job based on a time schedule. Once you have installed the packages, you can install cron as a Windows Service using cygrunsrv.

```
cygrunsrv --install cron --path /usr/sbin/cron --args –n
```
 
If you want to schedule the archiving time as 10:10 pm every day, you can edit the config file as:

```
crontab -e 
```

```
30 10 * * * python //path_for_sequdas_client/sequdas_client.py
```

### Data Analyzer

```
python sequdas_server.py
```


```
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

```

### Web application
An example for viewing report:

<img src="https://github.com/duanjunhyq/sequdas/blob/master/docs/images/sequdas_index_ex.png" width="900" height="700">



## Acknowledgments
Our implementation of uploading data to IRIDA utilizes code from [IRIDA miseq uploader](https://github.com/phac-nml/irida-miseq-uploader).

## Contributors
Jun Duan: Jun.Duan@bccdc.ca

Dan Fornika: Dan.Fornika@bccdc.ca

Damion Dooley: Damion.Dooley@bccdc.ca 

William Hsiao (PI): William.Hsiao@bccdc.ca 

