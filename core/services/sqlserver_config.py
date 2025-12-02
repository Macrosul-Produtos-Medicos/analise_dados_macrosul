from django.conf import settings

class SQLServerConfig:
    def __init__(self):
        self.driver = settings.SQLSERVER_DRIVER
        self.host = settings.SQLSERVER_HOST
        self.database = settings.SQLSERVER_DB
        self.port = settings.SQLSERVER_PORT
        self.user = settings.SQLSERVER_USER
        self.password = settings.SQLSERVER_PASSWORD
        
    def get_connection_string(self):
        return 'DRIVER='+self.driver+';SERVER='+self.host+','+str(self.port)+';DATABASE='+self.database+';UID='+self.user+';PWD='+self.password+';PORT='+str(self.port)+';'