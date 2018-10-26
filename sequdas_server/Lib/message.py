import smtplib



def send_email_core(user, pwd, recipient, subject, body):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo() # optional, called by login()
        server_ssl.login(gmail_user, gmail_pwd)  
        server_ssl.sendmail(FROM, TO, message)
        server_ssl.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
#################################################     


def send_email(user, pwd, recipient, subject, run_id,status):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    if subject =="system time error":
        body="The time setting on Sequencing PC is wrong. The automatic processes won't be triggered before this issue has been fixed. If you have any question, please contact William.hsiao@bccdc.ca "
        send_email_core(user, pwd, recipient, subject, body)
    if subject =="MySQL connection error":
        body="These is a issue with MySQL connect. The automatic processes won't be triggered before this issue has been fixed. If you have any question, please contact William.hsiao@bccdc.ca "
        send_email_core(user, pwd, recipient, subject, body)
    if subject =="Run failed":
        body="Your MiSeq run "+run_id+" generated some error. It will not be transferred to our archival server.  Please check the MiSeq instrument directly to decide if the run needs to be archived manually.  If you have any question, please contact William.hsiao@bccdc.ca"
        send_email_core(user, pwd, recipient, subject, body)
    if subject =="Starting":
        subject="Your MiSeq data is transferring to Sabin"
        body = "".join([
                   "Dear Colleagues,",
                   '\n\n',
                   "Your MiSEQ Run (",
                   run_id,
                   ")",
                   " is completed without error. It is being transferred to our archival server.  We will notify you once the transfer is completed. You can also check the status at http://142.103.74.210/miseq/. If you have any question, please contact William.hsiao@bccdc.ca."
                   ])
        send_email_core(user, pwd, recipient, subject, body)
    if subject =="Data archiving finished":
        subject="Data archiving finished, waiting for QC report"
        body = "".join([
                       "Dear Colleagues,",
                       '\n\n',
                       "Your MiSEQ Run (",
                        run_id,
                        ")",
                       " is completed without error and has been transferred to our archival server. The QC report pipeline is running.  We will notify you once the analysis is completed. You can also check the status at http://142.103.74.210/miseq/. If you have any question, please contact William.hsiao@bccdc.ca."
                      ])
        send_email_core(user, pwd, recipient, subject, body)    
    if subject =="Analysis is finished":
        subject="Analysis is done.Please check the results on SeqUDAS website"
        body = "".join([
                       "Dear Colleagues,",
                       '\n\n',
                       "Your MiSEQ Run (",
                        run_id,
                        ")",
                       " is completed without error and the analysis pipeline has been finished.Please check the report at http://142.103.74.210/miseq/. If you have any question, please contact William.hsiao@bccdc.ca."
                      ])
        send_email_core(user, pwd, recipient, subject, body)



