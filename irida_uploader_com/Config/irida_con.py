import ConfigParser
import os
import sys
def irida_config():
    try:
        config=read_config()
        confdict = {section: dict(config.items(section)) for section in config.sections()}
        return confdict
    except Exception as e :
        print(str(e),' Could not read configuration file')

def read_config():
    config = ConfigParser.RawConfigParser()
    pathname = os.path.dirname(os.path.abspath(sys.argv[0]))
    configFilePath = pathname+"/"+"config.ini"
    try:
        config.read(configFilePath)
        return config
    except Exception as e :
        print(str(e))