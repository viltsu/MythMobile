import os
from MythTV import MythDB


myDBHostName = 'localhost'
myDBName = 'mythconverg'
myDBUserName = 'mythtv'
myDBPassword = 'mythtv'

mythtvMyConfig = "/etc/mythtv/mysql.txt"

def loadConfig():
    """Load mysql configuration from MythTV mysql.txt settings file"""
    global myDBHostName, myDBName, myDBUserName, myDBPassword
    if os.path.exists(mythtvMyConfig):
        try:
            file = open(mythtvMyConfig)
        except:
            return
        key = []
        value = []

        for line in file:
            try:
                key, value = line.strip().split('=', 1)
            except:
                pass

            if 'DBHostName' in key:
                myDBHostName = value.strip()
            if 'DBUserName' in key:
                myDBUserName = value.strip()
            if 'DBName' in key:
                myDBName = value.strip()
            if 'DBPassword' in key:
                myDBPassword = value.strip()
        file.close()

loadConfig()

mythDB = MythDB(args = (('DBHostName', myDBHostName),
                        ('DBName', myDBName),
                        ('DBUserName', myDBUserName),
                        ('DBPassword', myDBPassword)))

mythtv_frontends = {}

def FEConnect(host):
    if host in mythtv_frontends:
        return True
    try:
        mythtv_frontends[host] = mythDB.getFrontend(host)
    except:
        return False
    return True
