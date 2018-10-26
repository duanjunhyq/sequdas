import MySQLdb
from Lib.core import *
s_config=sequdas_config()
mysql_host=s_config['mysql_account']['mysql_host']
mysql_user=s_config['mysql_account']['mysql_user']
mysql_passwd=s_config['mysql_account']['mysql_passwd']
mysql_db=s_config['mysql_account']['mysql_db']

def doInsert(bccdc_id_value,source_value,fullpath_value,folder_value,status_value,start_time_value,sample_infor) :
	myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
	cur = myConnection.cursor()
	end_time_value=""
	analysis_status_valuy=""
	cur.execute("INSERT INTO status_table (bccdc_id,source,fullpath,folder,status,start_time,end_time,sample,analysis_status,del_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(bccdc_id_value,source_value,fullpath_value,folder_value,status_value,start_time_value,end_time_value,sample_infor,analysis_status_valuy,"0"))
	myConnection.commit()
	myConnection.close()

def doUpdate(bccdc_id_value,status_value):
		myConnection = MySQLdb.connect( host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
		timestamp = time.strftime("%Y-%m-%d#%H:%M:%S")
		cur = myConnection.cursor()
		cur.execute(("UPDATE status_table SET status=%s,end_time=%s WHERE bccdc_id=%s"),(status_value,timestamp,bccdc_id_value))
		myConnection.commit()
		myConnection.close()